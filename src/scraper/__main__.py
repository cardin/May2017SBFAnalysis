import os
from random import random
import re
import time
from typing import List

import ProjUtils
from objects.Block import Block
from objects.FlatType import FlatType
from Hdb import Hdb


THROTTLE: float = 1.5
""" Throttle speed during web scraping, in seconds """

SAFE_FOLDER_PATH_REGEX = re.compile(r'[\\/]')
""" Regex used to detect portions of paths that needs to be
    sanitized into comma during serialisation """


def _get_file_path(town: str, flat_type: FlatType) -> str:
    """
    Returns a filepath corresponding to the requested parameters

    Args:
        town (str): The target town. Human-readable form (e.g. Ang Mo Kio)
        flat_type (FlatType): The target flat type.

    Returns:
        str: Absolute path to the location to save at
    """
    # format flat type
    town_label = SAFE_FOLDER_PATH_REGEX.sub(',', town)
    flat_type_label = SAFE_FOLDER_PATH_REGEX.sub(',', flat_type.label)

    data_path = os.path.join(os.getcwd(), 'data',
                             'json', town_label, '{}.json'.format(flat_type_label))
    return data_path


def _is_completed(town: str, flat_type: FlatType) -> bool:
    """
    Checks if the particular `town` and `flat_type` has been scraped yet

    Args:
        town (str): The target town. Human-readable form (e.g. Ang Mo Kio)
        flat_type (FlatType): The target flat type.

    Returns:
        bool: Whether the specified parameters have been web-scraped yet
    """
    json_path = _get_file_path(town, flat_type)
    return os.path.exists(json_path)


def main() -> None:
    """
    Main function
    """
    ProjUtils.set_project_cwd()

    hdb = Hdb()
    # for each Town
    towns = hdb.get_towns()
    print(towns)
    for i, town in enumerate(towns):
        print('------------------------------------')
        i_percent = float(i) / len(towns)
        print('Running town - {} ({:.0%})\n'.format(town, i_percent))

        # for each Flat Type
        flat_types = hdb.get_flat_types(town)
        print('\t{}'.format(flat_types))
        for j, flat_type in enumerate(flat_types):
            print('\t- - - - - - - - - - - - - - - - - -')
            j_percent = float(j) / len(flat_types)
            print('\tRunning flat type - {} ({:.0%}) + ({:.0%})\n'
                  .format(flat_type, i_percent, j_percent))

            # skip this Town and Flat Type if it is scraped already
            if not _is_completed(town, flat_type):
                blocks = []

                # Scraping each block
                block_codes = hdb.get_blocks(town, flat_type)
                print('\t\t{}'.format(block_codes))
                for k, block_code in enumerate(block_codes):
                    k_percent = float(k) / len(block_codes)
                    print('\t\tScraping {} ({:.0%}) + ({:.0%}) + ({:.0%}) ...'.format(
                        block_code, i_percent, j_percent, k_percent))

                    start_time = time.time()
                    block = hdb.get_block_details(town, flat_type, block_code)
                    blocks.append(block)
                    print('\t\tDone in {:2f} secs\n'.format(
                        time.time() - start_time))
                _serialize_blocks(town, flat_type, blocks)

                # Throttle the scraping
                time.sleep(random() * THROTTLE)
            else:
                print('\t\t Already done, skipping ...\n')


def _serialize_blocks(town: str, flat_type: FlatType, blocks: List[Block]) -> None:
    """
    Saves the blocks to disk

    Args:
        town (str): The target town. Human-readable form (e.g. Ang Mo Kio)
        flat_type (FlatType): The target flat type.
        blocks (list): List of `Block`s to serialize to disk
    """
    # JSON serialisation
    json_path = _get_file_path(town, flat_type)
    json_folder = os.path.dirname(json_path)
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    with open(json_path, 'w') as file:
        file.write('[')
        for i, block in enumerate(blocks):
            if i is not 0:
                file.write(',\n')
            file.write(block.to_json())
        file.write(']\n')
        file.close()


if __name__ == '__main__':
    main()
    input('Press any key to exit')
    exit(0)
