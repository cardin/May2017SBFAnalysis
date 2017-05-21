import os
import pickle
import re
import time
from random import random
from enum import Enum

from Hdb import Hdb

THROTTLE = 1.5  # seconds
SAFE_FOLDER_PATH_REGEX = re.compile(r'[\\/]')


class DataFormat(Enum):
    """
    Class for choice of output data format
    """
    JSON = 0
    PICKLE = 1


def _set_project_cwd():
    """ Changes current working directory to project level folder """
    curr_dir = os.getcwd()
    while os.path.basename(curr_dir) != 'May2017SBFAnalysis':
        curr_dir = os.path.dirname(curr_dir)
    os.chdir(curr_dir)


def _get_file_path(data_format, town, flat_type):
    """
    Returns a filepath corresponding to the requested parameters
    """
    file_path = None

    # format flat type
    town_label = SAFE_FOLDER_PATH_REGEX.sub(',', town)
    flat_type_label = SAFE_FOLDER_PATH_REGEX.sub(',', flat_type.label)

    data_path = os.path.join(os.getcwd(), 'data')
    if data_format is DataFormat.JSON:
        file_path = os.path.join(
            data_path, 'json', town_label, '{}.json'.format(flat_type_label))
    elif data_format is DataFormat.PICKLE:
        file_path = os.path.join(
            data_path, 'pickle', town_label, flat_type_label)
    else:
        raise ValueError(
            '"format"({}) was not part of Enumeration'.format(data_format))
    return file_path


def _is_completed(town, flat_type):
    """ Checks if the particular town and flat type has been scraped yet """
    json_path = _get_file_path(DataFormat.JSON, town, flat_type)
    pickle_path = _get_file_path(DataFormat.PICKLE, town, flat_type)
    return os.path.exists(json_path) and os.path.exists(pickle_path)


def main():
    """ Main function """
    _set_project_cwd()

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

    input('Press any key to exit')
    exit(0)


def _serialize_blocks(town, flat_type, blocks):
    """ Saves the blocks to disk """
    # JSON serialisation
    json_path = _get_file_path(DataFormat.JSON, town, flat_type)
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

    # Pickle serialisation
    pickle_path = _get_file_path(DataFormat.PICKLE, town, flat_type)
    pickle_folder = os.path.dirname(pickle_path)
    if not os.path.exists(pickle_folder):
        os.makedirs(pickle_folder)

    with open(pickle_path, 'wb') as file:
        pickle.dump(blocks, file)


if __name__ == '__main__':
    main()
