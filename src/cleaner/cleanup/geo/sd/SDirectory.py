import json
from os import path
from typing import ClassVar, Dict, Optional

from selenium import webdriver

import ProjUtils
from ..Geocode import Geocode
from ..IGeoservice import IGeoservice


class SDirectory(IGeoservice):
    """
    Client for accessing Street Directory API

    Attributes:
        _driver (webdriver.PhantomJS): Selenium webdriver
    """

    _PHANTOMJS_PATH: ClassVar[str] = r'lib\phantomjs-2.1.1-windows\bin\phantomjs.exe'
    # Path to PhantomJS
    _HTML_LOC: ClassVar[str] = 'SDirectory.html'
    # Filename of HTML loader for JS script

    _driver: webdriver.PhantomJS

    def __init__(self) -> None:
        full_path = path.join(ProjUtils.get_project_path(),
                              SDirectory._PHANTOMJS_PATH)
        self._driver = webdriver.PhantomJS(executable_path=full_path)

    def geocode(self, address: str) -> Optional[Geocode]:
        """
        Obtains the lat and long of an address

        Args:
            address (str): Human readable address

        Returns:
            Optional[Geocode]: Geocode result
        """
        uri = 'file:///{}?g={}'.format(path.join(ProjUtils.get_curr_folder_path(),
                                                 SDirectory._HTML_LOC), address)
        res = self._submit_query(uri)

        result: Optional[Geocode] = None
        try:
            # try to favor the right postal code
            block = address.split(' ')[0]
            if block[-1].isalpha():
                block = block[:-1]

            target_bldg = next(
                (_ for _ in res if 'pc' in _ and _['pc'][-3:] == block))
            result = self._json2geocode(target_bldg)
        except StopIteration:
            try:
                # try to favor results that contain the word 'HDB'
                target_bldg = next(
                    (_ for _ in res if 'a' in _ and
                     't' in _ and 'HDB' in _['t']))
                result = self._json2geocode(target_bldg)
            except StopIteration:
                try:
                    target_bldg = next(
                        (_ for _ in res if 'a' in _ and 't' in _))
                    result = self._json2geocode(target_bldg)
                except StopIteration:
                    pass
        return result

    def geocode_reverse(self, block: str, street: str) -> Geocode:
        """
        Geocodes the street name, and reverse geocodes for a building around it.
        Hopefully the building is found (but very unlikely)

        Args:
            block (str): The block number
            street (str): The street name

        Returns:
            Optional[Geocode]: Geocode result
        """
        # get street lat/long
        uri = 'file:///{}?g={}'.format(path.join(
            ProjUtils.get_curr_folder_path(), SDirectory._HTML_LOC), street)
        res = self._submit_query(uri)
        if res[0]['total'] == 0:
            return None
        street_lat = float(res[1]['y'])
        street_lng = float(res[1]['x'])

        # get buildings around it
        uri = 'file:///{}?r={},{}'.format(
            path.join(ProjUtils.get_curr_folder_path(), SDirectory._HTML_LOC),
            street_lat, street_lng)
        res = self._submit_query(uri)

        # identify the right building
        if res['no.'] != block:
            return None
        return self._json2geocode(res)

    def close(self) -> None:
        """
        Closes the WebDriver
        """
        self._driver.close()

    def _submit_query(self, uri: str) -> Dict:
        self._driver.get(uri)
        res = self._driver.find_element_by_id('query_results').text
        return json.loads(res)

    @staticmethod
    def _json2geocode(result: Dict) -> Geocode:
        title = result['t'] if 't' in result else ''
        postal = int(result['pc'] if 'pc' in result else 0)
        lat = float(result['y'])
        long = float(result['x'])
        return Geocode(title, lat, long, postal)
