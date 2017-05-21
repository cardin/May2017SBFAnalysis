import json
from typing import ClassVar, Dict, Optional

import requests

from ..Geocode import Geocode
from ..IGeoservice import IGeoservice
from .OneMapAuth import OneMapAuth


class OneMap(IGeoservice):
    """
    Client for accessing OneMap API
    """

    _GEOCODE_API: ClassVar[str] = r'https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1'  # pylint: disable=line-too-long
    _R_GEOCODE_API: ClassVar[str] = r'https://developers.onemap.sg/privateapi/commonsvc/revgeocode?location={},{}&token={}&buffer=500&addressType=HDB'  # pylint: disable=line-too-long

    def geocode(self, address: str) -> Optional[Geocode]:
        """
        Obtains the lat and long of addresses

        Args:
            address (str): Human readable address

        Returns:
            Optional[Geocode]: Geocode result
        """
        # query
        uri = self._GEOCODE_API.format(address)
        req = requests.get(uri)
        res = json.loads(req.text)

        # parse
        result: Optional[Geocode]
        if res['found'] > 0:
            # find the right building
            block = address.split(' ', 1)[0]
            target_bldg: Optional[Dict] = None
            for bldg in res['results']:
                if bldg['BLK_NO'] == block:
                    target_bldg = bldg
                    break
            if not target_bldg:
                target_bldg = res['results'][0]

            result = self._json2geocode(target_bldg)
        else:
            result = None
        return result

    def geocode_reverse(self, block: str, street: str) -> Optional[Geocode]:
        """
        Geocodes the street name, and reverse geocodes for buildings around it.
        Hopefully the building is then found

        Args:
            block (str): The block number
            street (str): The street name

        Returns:
            Optional[Geocode]: Geocode result
        """
        # get street lat/long
        uri = self._GEOCODE_API.format(street)
        req = requests.get(uri)
        res = json.loads(req.text)
        if res['found'] == 0:
            return None
        street_lat = float(res['results'][0]['LATITUDE'])
        street_lng = float(res['results'][0]['LONGITUDE'])

        # get buildings around it
        token = OneMapAuth.get_token()
        uri = self._R_GEOCODE_API.format(street_lat, street_lng, token)
        req = requests.get(uri)
        res = json.loads(req.text)

        # identify the right building
        target_bldg: Optional[Dict] = None
        for bldg in res['GeocodeInfo']:
            if bldg['BLOCK'] == block:
                target_bldg = bldg

        if not target_bldg:
            return None
        return self._json2geocode(target_bldg)

    @staticmethod
    def _json2geocode(result: Dict) -> Geocode:
        bldg = result['BUILDING'] if 'BUILDING' in result else ''
        lat = float(result['LATITUDE'])
        lng = float(result['LONGITUDE'])
        postal = int(result['POSTAL']) if 'POSTAL' in result else 0
        return Geocode(bldg, lat, lng, postal)
