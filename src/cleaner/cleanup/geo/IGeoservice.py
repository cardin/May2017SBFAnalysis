import abc
from typing import Optional

from .Geocode import Geocode


class IGeoservice(object, metaclass=abc.ABCMeta):
    """
    Abstract class for inheritance.
    Instance methods in case connection is optimized for statefulness
    """
    @abc.abstractmethod
    def geocode(self, address: str) -> Optional[Geocode]:
        pass

    @abc.abstractmethod
    def geocode_reverse(self, block: str, street: str) -> Optional[Geocode]:
        pass
