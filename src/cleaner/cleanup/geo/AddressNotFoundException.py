class AddressNotFoundException(Exception):
    """
    Exception for when an address cannot be geocoded
    """

    def __init__(self, address: str) -> None:
        Exception.__init__(
            self, 'This address was not found: {}'.format(address))
