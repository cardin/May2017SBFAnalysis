from typing import Optional


class LeasePrice(object):
    """
    Tuple for lease term and price

    Attributes:
        price (int): price of the given `lease`
        lease (str, optional): lease. May be no. of years, or 'Remaining' for remaining time.
    """

    def __init__(self, price: int, lease: Optional[str] = None) -> None:
        self.lease = lease
        self.price = price

    @staticmethod
    def scrape(lease_price: str) -> 'LeasePrice':
        """
        Constructor for scraper

        Args:
            lease_price (str): scraped pair of lease and price (e.g. $170,000 - 17 Years)

        Returns:
            LeasePrice: An instance of `LeasePrice` created from the string `lease_price`
        """
        price_strip = lease_price.strip()

        # If Lease and Price
        result = None
        if '-' in price_strip:
            price_split = price_strip.split('-')
            price = int(price_split[0].strip()[1:].replace(',', ''))
            lease = price_split[1].strip().split(' ')[0]
            result = LeasePrice(price, lease)
        else:  # Price only
            price = int(price_strip[1:].replace(',', ''))
            result = LeasePrice(price)
        return result

    def __str__(self) -> str:
        return '${0:,} - {1} Years'.format(self.price, self.lease)

    def __repr__(self) -> str:
        return self.__str__()
