import re
from typing import List

from .LeasePrice import LeasePrice


class Apartment(object):
    """
    Apartment object.

    Attributes:
        floor (int): Floor number.
        unit (int): Unit number.
        area (float): Area in sqm.
        lease_price_list (list of LeasePrice): List of price per lease period
        is_repurchased (bool): Is it repurchased?
    """
    floor: int
    unit: int
    area: float
    lease_price_list: List[LeasePrice]
    is_repurchased: bool

    def __init__(self, floor: int, unit: int, area_sqm: float,
                 lease_price_list: List[LeasePrice], is_repurchased: bool) -> None:
        """ Constructor """
        self.floor = floor
        self.unit = unit
        self.area = area_sqm
        self.lease_price_list = lease_price_list
        self.is_repurchased = is_repurchased

    @staticmethod
    def scrape(apartment_num: str, area_list: str) -> 'Apartment':
        """
        Constructor for scraper

        Args:
            apartment_num (str): Scraped apartment number (e.g. #17-01*)
            area_list (str): Scraped string containing price, lease and area

        Returns:
            Apartment: An instance of `Apartment`
        """

        # is_repurchased
        apartment_num = apartment_num.strip()
        is_repurchased = apartment_num.endswith('*')
        if is_repurchased:
            apartment_num = apartment_num[:-1]

        # Floor, unit
        apartment_num_split = apartment_num[1:].split('-')
        floor = int(apartment_num_split[0])
        unit = int(apartment_num_split[1])

        # Area, Price, Lease
        area_price = area_list.strip().split(r'<br/>')
        raw_area = area_price[-1]
        raw_price = area_price[:-2]
        area = float(re.match(r'^(\d+)', raw_area).groups()[0])
        lease_prices = [LeasePrice.scrape(_) for _ in raw_price]

        return Apartment(floor, unit, area, lease_prices, is_repurchased)

    def __str__(self) -> str:
        return '#{:0=2d}-{}{}, {} Sqm, {}' \
            .format(self.floor, self.unit,
                    '(R)' if self.is_repurchased else '', self.area,
                    self.lease_price_list)

    def __repr__(self) -> str:
        return self.__str__()
