from os import path
import pickle
from typing import ClassVar, Dict, List, Optional

import ProjUtils
from .AddressNotFoundException import AddressNotFoundException
from .Geocode import Geocode
from .onemap.OneMap import OneMap
from .sd.SDirectory import SDirectory


class Geocoding(object):
    """
    Uses various geocoding services with caching.

    Services:
        OneMap
        Street Directory

    Order of query:
        Geocode Block number + Street
        Geocode Block number without alphabets + Street
        Geocode Street + Reverse Geocode + filter block number
        Geocode Street
    """
    _GEOCACHE_LOC: ClassVar[str] = 'Geocoding.cache'
    _THROTTLE: float = 0.05
    # Throttle in seconds
    _geocache: ClassVar[Dict] = {}

    @classmethod
    def geocode(cls, *addresses: str) -> List[Geocode]:
        """
        Obtains the lat and long of an address

        Args:
            addresses (str): Human readable addresses

        Returns:
            List[Geocode]: Geocode results
        """
        onemap = OneMap()
        sdir = SDirectory()
        cls._load_cache()

        results = []
        for address in addresses:
            if address not in cls._geocache:
                result = cls._basic_geocode(address, onemap, sdir)
                if not result:
                    result = cls._no_alpha_geocode(address, onemap, sdir)
                    if not result:
                        result = cls._geocode_reverse(address, onemap, sdir)
                cls._geocache[address] = result
            results.append(cls._geocache[address])

        cls._save_cache()
        sdir.close()
        return results

    @classmethod
    def _load_cache(cls) -> None:
        """
        Loads geocache from file into class variable
        """
        geocache_loc = path.join(
            ProjUtils.get_curr_folder_path(), cls._GEOCACHE_LOC)
        if path.exists(geocache_loc):
            with open(geocache_loc, 'rb') as fstream:
                cls._geocache = pickle.load(fstream)
        else:
            cls._geocache = {}

    @classmethod
    def _save_cache(cls) -> None:
        """
        Saves geocache to file
        """
        geocache_loc = path.join(
            ProjUtils.get_curr_folder_path(), cls._GEOCACHE_LOC)
        with open(geocache_loc, 'wb') as fstream:
            pickle.dump(cls._geocache, fstream)

    @classmethod
    def _basic_geocode(cls, address: str, onemap: OneMap, sdir: SDirectory) -> Optional[Geocode]:
        result = onemap.geocode(address)
        if not result:
            result = sdir.geocode(address)
        return result

    @classmethod
    def _no_alpha_geocode(cls, address: str, onemap: OneMap, sdir: SDirectory) -> Optional[Geocode]:
        # Gets the simplified address with no block alphabets
        split_addr = address.split(' ', 1)
        block, street = (split_addr[0], split_addr[1])
        if block[-1].isalpha():
            no_alpha_addr = ' '.join((block[:-1], street))
        else:
            return None
        return cls._basic_geocode(no_alpha_addr, onemap, sdir)

    @classmethod
    def _geocode_reverse(cls, address: str, onemap: OneMap, sdir: SDirectory) -> Optional[Geocode]:
        # Gets the street and block number as separate elements
        split_addr = address.split(' ', 1)
        block, street = (split_addr[0], split_addr[1])

        result = onemap.geocode_reverse(block, street)
        if not result:
            result = sdir.geocode_reverse(block, street)
            if not result:
                raise AddressNotFoundException(address)
        print('[Warning] {} is via geocode_reverse()'.format(address))
        return result
