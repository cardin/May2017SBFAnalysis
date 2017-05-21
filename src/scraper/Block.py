import json
from typing import List, Tuple, Union

from Apartment import Apartment
from BlockCode import BlockCode
from FlatType import FlatType


class Block(object):
    """
    A HDB Block

    Attributes:
        town (str): The town that the block belongs to (e.g. Ang Mo Kio)
        flat_type (FlatType): The type of flat the block is
        block_code (BlockCode): Specific HDB codes for the block, including its block number

        street (str): The street that the block is on (e.g. Ang Mo Kio Ave 1)
        pcd_date (str): Probable Completion Date. Format uncertain
        dpd_date (str): Delivery Possession Date. Format uncertain
        lcd_date (str): Lease Commencement Date. Format uncertain

        quota_chinese (int): Available slots for Chinese residents
        quota_malay (int): Available slots of Malay residents
        quota_other (int): Available slots for residents of other ethnicities

        apartments (list of Apartment): List of available apartments
    """

    def __init__(self, town: str, flat_type: FlatType, block_code: BlockCode,
                 street: str, pcd_date: str, dpd_date: str, lcd_date: str,
                 quota_chinese: int, quota_malay: int, quota_other: int,
                 apartments: List[Apartment]) -> None:
        self.town = town
        self.flat_type = flat_type
        self.block_code = block_code

        self.street = street
        self.pcd_date = pcd_date
        self.dpd_date = dpd_date
        self.lcd_date = lcd_date

        self.quota_chinese = quota_chinese
        self.quota_malay = quota_malay
        self.quota_other = quota_other

        self.apartments = apartments

    @staticmethod
    def scrape(town: str, flat_type: FlatType, block_code: BlockCode,
               block_details: Tuple[str, str, str, str, str],
               apt_details: Tuple[str, str]) -> 'Block':
        """
        Constructor for scraper

        Args:
            town (str): The town that the block belongs to (e.g. Ang Mo Kio)
            flat_type (FlatType): The type of flat the block is
            block_code (BlockCode): Specific HDB codes for the block, including its block number

            block_details (tuple): Tuple of strings containing the street,
                                    PCD, DPD and LCD dates of the block
            apt_details (tuple): Tuple of strings containing the raw apartment number
                                    and lease pricing

        Returns:
            Block: An instance of `Block` holding the scraped values
        """
        town = town.replace('+', ' ')

        street = block_details[0]
        pcd_date = block_details[1]
        dpd_date = block_details[2]
        lcd_date = block_details[3]
        if lcd_date.endswith('#'):
            lcd_date = lcd_date[:-1].strip()

        quota = block_details[4].split(',')
        quota.sort()
        quota_chinese = int(quota[0].split('-')[-1].strip())
        quota_malay = int(quota[1].split('-')[-1].strip())
        quota_other = int(quota[2].split('-')[-1].strip())

        apartments = [Apartment.scrape(*_) for _ in apt_details]

        return Block(town, flat_type, block_code,
                     street, pcd_date, dpd_date, lcd_date,
                     quota_chinese, quota_malay, quota_other, apartments)

    # pragma pylint: disable=unnecessary-lambda
    def to_json(self) -> str:
        """
        To JSON

        Returns:
            str: JSON string serialisation. One-way.
        """
        return json.dumps(self, default=lambda o: Block._try_json(o), sort_keys=True,
                          indent=4)
    # pragma pylint: enable=unnecessary-lambda

    # pragma pylint: disable=bare-except
    @staticmethod
    def _try_json(obj: object) -> Union[str, dict]:
        result = None
        try:
            result = obj.__dict__
        except:
            result = str(obj)
        return result

    # pragma pylint: enable=bare-except

    def __str__(self) -> str:
        return self.to_json()

    def __repr__(self) -> str:
        return self.__str__()
