import re

from bs4 import BeautifulSoup
import requests

from FlatType import FlatType
from Block import Block
from BlockCode import BlockCode


class Hdb(object):
    """
    API:
    * selection/Flat_Type = SBF (Sale of Balance)
    * dteBallot = (which period of ballot it is)

    * ethnic = (Y - all, M - malay, C - chinese, O - indian/others)
    * ViewOption = (A - all, 2 - booked, 1 - not booked)
    * DesType = (flat category, e.g. 3-room premium) (A - all)

    * Town = (the town)
    * Flat = (flat type, e.g. 3 room, 4 room)
    """
    HOME_PAGE = r'https://services2.hdb.gov.sg/webapp/BP13AWFlatAvail/BP13EBSFlatSearch?' \
                r'Flat_Type=SBF&dteBallot=201705&ethnic=Y&ViewOption=1&DesType=A'

    def __init__(self):
        self.__towns__ = None
        self.session = requests.Session()

    def get_towns(self):
        """ Returns a list of HDB towns available for SBF """
        if self.__towns__ is None:
            # HTTP Request
            resp = self.session.get(Hdb.HOME_PAGE).content
            soup = BeautifulSoup(resp, 'html.parser')

            # Extract
            town_dropdown = soup.find(
                'form', id='flatSummary').find('select', id='Town')
            options = town_dropdown.find_all('option')

            self.__towns__ = [_['value'] for _ in options]
        return self.__towns__

    def get_flat_types(self, town):
        """ Returns a list of HDB flat types available for SBF """

        # HTTP Request
        town = town.replace(' ', '+')
        uri = '{0}&Town={1}'.format(Hdb.HOME_PAGE, town)
        resp = self.session.get(uri).content
        soup = BeautifulSoup(resp, 'html.parser')

        # Extract
        types = soup.find('form', id='flatSummary').find('select', id='Flat')
        options = types.find_all('option')
        return [FlatType(_['value'], _.text) for _ in options]

    def get_blocks(self, town, flat_type):
        """ Returns a list of available blocks in the HDB town """
        blocks = []

        # HTTP Request
        town = town.replace(' ', '+')
        uri = '{0}&Town={1}&Flat={2}'.format(
            Hdb.HOME_PAGE, town, flat_type.code)
        resp = self.session.get(uri).content
        soup = BeautifulSoup(resp, 'html.parser')

        # Extract
        cells = soup.find('div', id='blockDetails').find(
            'table').find_all('td')
        for cell in cells:
            jscript = cell.find('div')['onclick']
            re_result = re.search(r"'(\w+)','(\w+)','(\w+)'", jscript)
            block = BlockCode(*(re_result.groups()[:3]))
            blocks.append(block)
        return blocks

    def get_block_details(self, town, flat_type, block_code):
        """ Returns in-depth details for a specific HDB block """
        # HTTP Request
        town = town.replace(' ', '+')

        uri = '{0}&Town={1}&Flat={2}&Block={3}&Neighbourhood={4}&Contract={5}' \
            .format(Hdb.HOME_PAGE, town, flat_type.code,
                    block_code.block_num, block_code.neighbourhood, block_code.contract)

        resp = self.session.get(uri).content
        soup = BeautifulSoup(resp, 'html.parser')

        # Test if extraction will succeed
        soup = self.__check_block_details_exist__(town, flat_type, uri, soup)

        # Extract block details
        target_div = soup.find('div', id='blockDetails')

        street = Hdb.__get_block_details__(target_div, 'Street')
        pcd_date = Hdb.__get_block_details__(
            target_div, 'Probable Completion Date')
        dpd_date = Hdb.__get_block_details__(
            target_div, 'Delivery Possession Date')
        lcd_date = Hdb.__get_block_details__(
            target_div, 'Lease Commencement Date')
        ethnic_quota = Hdb.__get_block_details__(
            target_div, 'Available Ethnic Quota')
        block_details = (street, pcd_date, dpd_date, lcd_date, ethnic_quota)

        # Extract apartment details
        apartment_thead = target_div.find(
            text=re.compile('Mouseover.?unit.?number'))
        apartment_td = apartment_thead.find_all_next('td')
        apartments_details = []
        for td_tag in apartment_td:
            font_tag = td_tag.find('font')

            apartment_num = font_tag['id']
            area_price = font_tag['title']
            apartments_details.append((apartment_num, area_price))

        block_obj = Block.scrape(
            town, flat_type.label, block_code, block_details, apartments_details)
        return block_obj

    def __check_block_details_exist__(self, town, flat_type, uri, soup):
        """
        This checks if the block details exist on the site.
        Because the site only displays if the pages are visited in a certain order.
        """

        # Perform check
        target_div = soup.find('div', id='blockDetails')
        street_tag = target_div.find(text='Street')

        # Request the url again to prime the session variables
        # For some reason, directly visiting the page will fail
        # Btw, setting HTTP Referer doesn't work either
        if street_tag is None:
            prev_uri = '{0}&Town={1}&Flat={2}'.format(
                Hdb.HOME_PAGE, town, flat_type.code)
            self.session.get(prev_uri)
            resp = self.session.get(uri).content
            soup = BeautifulSoup(resp, 'html.parser')
        return soup

    @staticmethod
    def __get_block_details__(target_div, label):
        """ Returns block details using label as a search term """
        label = label.replace(' ', '.?')

        target_tag = target_div.find(text=re.compile(label))
        value = target_tag.find_next('div').text.strip()
        # find_next is positional, regardless of hierarchy
        return value
