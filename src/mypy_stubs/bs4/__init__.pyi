from re import Pattern
from typing import Optional, Union, Any


class BeautifulSoup():
    def __init__(self, content: Union[bytes, str], parser: str) -> None: ...

    def find(self, tag: Optional[str] = None,
             id: Optional[str] = None, text: Optional[Any] = None): ...


class Tag(BeautifulSoup):
    pass
