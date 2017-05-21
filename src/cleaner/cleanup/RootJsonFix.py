"""
Fixes the fact that the root element is an array.
Changes it to a JSON instead
"""
import json
import os
from os import path
from typing import Dict

from .objects.CleanupLog import CleanupLog

_PROCESS_NAME = 'RootJsonFix'


def run(json_loc: str, log_loc: str) -> None:
    """
    Changes root element from array to JSON

    Args:
        json_loc (str): location of JSON folder
        log_loc (str): location of cleaning log
    """
    if CleanupLog.has_done(_PROCESS_NAME, log_loc):
        print('Skipping {}'.format(_PROCESS_NAME))
        return

    # Iterate through all files
    print('--------------------------------')
    print('[RootJsonFix]')
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

                if isinstance(data, list):
                    # Resave the file
                    root_data = {'blocks': data}
                    with open(filepath, 'w') as fstream:
                        json.dump(root_data, fstream, indent=4)

    CleanupLog.log_done(_PROCESS_NAME, log_loc)
