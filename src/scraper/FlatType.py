class FlatType(object):
    """
    Tuple of Flat Type

    Attributes:
        code (str): Used in GET url request
        label (str): Human-readable version of `code`
    """

    def __init__(self, code: str, label: str) -> None:
        self.code = code
        self.label = label

    def __str__(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return self.__str__()
