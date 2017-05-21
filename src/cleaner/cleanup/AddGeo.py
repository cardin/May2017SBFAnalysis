"""
Adds geolocation data to the blocks
"""
import json
import os
from os import path
from typing import Dict

from .geo.Geocoding import Geocoding
from .objects.CleanupLog import CleanupLog

_PROCESS_NAME = 'AddGeo'


def run(json_loc: str, log_loc: str) -> None:
    """
    Adds details to the blocks, such as geolocation, etc.

    Args:
        json_loc (str): The JSON string to modify
        log_loc (str): location of cleaning log
    """
    if CleanupLog.has_done(_PROCESS_NAME, log_loc):
        print('Skipping {}'.format(_PROCESS_NAME))
        return

    # Iterate through all files
    print('--------------------------------')
    print('[AddGeo]')
    for root, _, filenames in os.walk(json_loc):
        if filenames:
            print('Running directory {}'.format(root))

            for filename in filenames:
                filepath = path.join(root, filename)

                # Open the file
                data: Dict
                with open(filepath, 'r') as fstream:
                    data = json.load(fstream)
                    fstream.close()

                if _add_geo(data):
                    # Resave the file
                    with open(filepath, 'w') as fstream:
                        json.dump(data, fstream, indent=4)
    CleanupLog.log_done(_PROCESS_NAME, log_loc)


def _add_geo(data: Dict) -> bool:
    """
    Adds geolocation to the blocks

    Args:
        data (Dict): The JSON of a file

    Returns:
        bool: Whether any changes were made
    """
    # skip if it's already done
    if 'lat' in data['blocks'][0]:
        return False

    # bulk process is faster
    addresses = [' '.join((blk['block_code']['block_num'], blk['street']))
                 for blk in data['blocks']]
    geocodes = Geocoding.geocode(*addresses)

    # manually iterate again
    for i, blk in enumerate(data['blocks']):
        geocode = geocodes[i]
        blk['title'] = geocode.title
        blk['lat'] = geocode.lat
        blk['long'] = geocode.long
        blk['postal'] = geocode.postal
    return True
