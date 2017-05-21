class Geocode(object):
    """
    Class for geocode results

    Attributes:
        title (str): Title name E.g. Teck Ghee View
        lat (float): Latitude
        long (float): Longitude
        postal (int): Postal Code
    """
    title: str
    lat: float
    long: float
    postal: int

    def __init__(self, title: str, lat: float, long: float, postal: int) -> None:
        self.title = title
        self.lat = lat
        self.long = long
        self.postal = postal

    def __str__(self) -> str:
        return '({},{},{},{})'.format(self.title, self.lat, self.long, self.postal)

    def __repr__(self) -> str:
        return self.__str__()
