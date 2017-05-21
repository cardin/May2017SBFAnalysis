import re
from typing import ClassVar, List, Optional

from bs4 import BeautifulSoup, Tag
import requests

from objects.FlatType import FlatType
from objects.Block import Block
from objects.BlockCode import BlockCode


class Hdb(object):
    """
    Object used to query and retrieve data using HDB's unofficial GET-based API

    HDB API:
        * selection/Flat_Type = SBF (Sale of Balance)
        * dteBallot = (which period of ballot it is)

        * ethnic = (Y - all, M - malay, C - chinese, O - indian/others)
        * ViewOption = (A - all, 2 - booked, 1 - not booked)
        * DesType = (flat category, e.g. 3-room premium) (A - all)

        * Town = (the town)
        * Flat = (flat type, e.g. 3 room, 4 room)

    Attributes:
        _town (Optional[List[str]]): Internal reference to list of towns
        _session (requests.Session): Keeps track of persistent session across URL requests
    """

    HOME_PAGE: ClassVar[str]
    _town: Optional[List[str]]
    _session: requests.Session

    HOME_PAGE = r'https://services2.hdb.gov.sg/webapp/BP13AWFlatAvail/BP13EBSFlatSearch?' \
        r'Flat_Type=SBF&dteBallot=201705&ethnic=Y&ViewOption=1&DesType=A'
    """ Basic HDB URL to perform queries on """

    def __init__(self) -> None:
        self._towns = None  # type: Optional[List[str]]
        self._session = requests.Session()

    def get_towns(self) -> Optional[List[str]]:
        """
        Retrieves a list of HDB towns available for SBF

        Returns:
            list: a list of HDB towns
        """
        if self._towns is None:
            # HTTP Request
            resp = self._session.get(Hdb.HOME_PAGE).content
            soup = BeautifulSoup(resp, 'html.parser')

            # Extract
            town_dropdown = soup.find(
                'form', id='flatSummary').find('select', id='Town')
            options = town_dropdown.find_all('option')

            self._towns = [_['value'] for _ in options]
        return self._towns

    def get_flat_types(self, town: str) -> List[FlatType]:
        """
        Retrieves a list of HDB flat types available for SBF

        Args:
            town (str): The target town. Human-readable form (e.g. Ang Mo Kio)

        Returns:
            list: List of `FlatType`s available in `town`
        """

        # HTTP Request
        town = town.replace(' ', '+')
        uri = '{0}&Town={1}'.format(Hdb.HOME_PAGE, town)
        resp = self._session.get(uri).content
        soup = BeautifulSoup(resp, 'html.parser')

        # Extract
        types = soup.find('form', id='flatSummary').find('select', id='Flat')
        options = types.find_all('option')
        return [FlatType(_['value'], _.text) for _ in options]

    def get_blocks(self, town: str, flat_type: FlatType) -> List[BlockCode]:
        """
        Retrieves a list of available blocks in the HDB town

        Args:
            town (str): The target town. Human-readable form (e.g. Ang Mo Kio)
            flat_type (FlatType): The target flat type.

        Returns:
            list: List of `BlockCode`s for the given `town` and `flat_type`
        """
        blocks = []

        # HTTP Request
        town = town.replace(' ', '+')
        uri = '{0}&Town={1}&Flat={2}'.format(
            Hdb.HOME_PAGE, town, flat_type.code)
        resp = self._session.get(uri).content
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

    def get_block_details(self, town: str, flat_type: FlatType, block_code: BlockCode) -> Block:
        """
        Retrieves in-depth details for a specific HDB block

        Args:
            town (str): The target town. Human-readable form (e.g. Ang Mo Kio)
            flat_type (FlatType): The target flat type.
            block_code (BlockCode): The target block, given as a `BlockCode`

        Returns:
            Block: Details about the given `town`, `flat_type` and `block_code`
        """
        # HTTP Request
        town = town.replace(' ', '+')

        uri = '{0}&Town={1}&Flat={2}&Block={3}&Neighbourhood={4}&Contract={5}' \
            .format(Hdb.HOME_PAGE, town, flat_type.code,
                    block_code.block_num, block_code.neighbourhood, block_code.contract)

        resp = self._session.get(uri).content
        soup = BeautifulSoup(resp, 'html.parser')

        # Test if extraction will succeed
        soup = self._check_block_details_exist(town, flat_type, uri, soup)

        # Extract block details
        target_div = soup.find('div', id='blockDetails')

        street = Hdb._get_block_details(target_div, 'Street')
        pcd_date = Hdb._get_block_details(
            target_div, 'Probable Completion Date')
        dpd_date = Hdb._get_block_details(
            target_div, 'Delivery Possession Date')
        lcd_date = Hdb._get_block_details(
            target_div, 'Lease Commencement Date')
        ethnic_quota = Hdb._get_block_details(
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

    def _check_block_details_exist(self, town: str, flat_type: FlatType,
                                   uri: str, soup: BeautifulSoup) -> BeautifulSoup:
        """
        This checks if the block details exist on the site.
        Because the site only displays if the pages are visited in a certain order.

        Args:
            town (str): The target town. Human-readable form (e.g. Ang Mo Kio)
            flat_type (FlatType): The target flat type.
            uri (str): The parameterized URI we are browsing to.
            soup (BeautifulSoup): The parser we are using to analyze

        Returns:
            BeautifulSoup: The new parser that we should use, to replace `soup`
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
            self._session.get(prev_uri)
            resp = self._session.get(uri).content
            soup = BeautifulSoup(resp, 'html.parser')
        return soup

    @staticmethod
    def _get_block_details(target_div: Tag, label: str) -> str:
        """
        Retrieves block details using label as a search term

        Args:
            target_div (Tag): A target `Tag` from BeautifulSoup
            label (str): The term we are searching for within `target_div`

        Return:
            str: The value associated with the `label` within `target_div`
        """
        label = label.replace(' ', '.?')

        target_tag = target_div.find(text=re.compile(label))
        value = target_tag.find_next('div').text.strip()
        # find_next() is positional, regardless of hierarchy
        return value
