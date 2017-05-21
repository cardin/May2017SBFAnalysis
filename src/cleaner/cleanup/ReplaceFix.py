"""
For a given property, finds matching values to replace with another value
"""

import json
import os
from os import path
#import threading
from typing import Dict, List

from .objects.CleanupLog import CleanupLog
from .objects.ReplacePair import ReplacePair

_PROCESS_NAME = 'ReplaceFix'


def run(json_loc: str, log_loc: str, replace_pair: ReplacePair) -> None:
    """
    For a given property, finds matching values to replace with another value

    Args:
        json_loc (str): Location of the JSON folder
        log_loc (str): location of cleaning log
        replace_pair (ReplacePair): Tuple to specify how and what to replace
    """
    process_name = ':'.join(
        (_PROCESS_NAME, replace_pair.prop_name, replace_pair.name))
    if CleanupLog.has_done(process_name, log_loc):
        print('Skipping {}'.format(process_name))
        return

    # Iterate through all files
    print('--------------------------------')
    print('[ReplaceFix] {}'.format(replace_pair.prop_arr))

    #thread_list = []
    for root, _, filenames in os.walk(json_loc):
        if filenames:
            _run_directory(root, filenames, replace_pair)
    #        # Benchmarked: No visible benefits, if not slower
    #        # PS 1: We run on directory, otherwise there's too many threads
    #        # PS 2: Can't use multiprocessing, because ReplacePair contains
    #        # a local lambda that is non-serialisable without using dill,
    #        # which is a slower pickle
    #        thr = threading.Thread(target=_run_directory, name=root,
    #                               args=(root, filenames, replace_pair))
    #        thr.start()
    #        thread_list.append(thr)

    # for thr in thread_list:
    #    thr.join()
    CleanupLog.log_done(process_name, log_loc)


def _run_directory(root: str, filenames: List[str], replace_pair: ReplacePair) -> None:
    """
    Runs on a single directory

    Args:
        filepath (str): The absolute filepath to run on
    """
    print('Running directory {}'.format(root))
    for filename in filenames:
        filepath = path.join(root, filename)

        # Open the file
        data: Dict
        with open(filepath, 'r') as fstream:
            data = json.load(fstream)
            fstream.close()

        if _clean_file(data, replace_pair):  # if modified
            # Save the file
            with open(filepath, 'w') as fstream:
                json.dump(data, fstream, indent=4)


def _clean_file(data: Dict, replace_pair: ReplacePair) -> bool:
    """
    Digs into a file to find matching attribute values and replaces them

    Args:
        data (dict): Dictionary (aka JSON)
        replace_pair (ReplacePair): Tuple to specify how and what to replace

    Returns:
        bool: Whether a change was made to `data`
    """
    is_dirty: bool = False

    # remove the top-level property
    replace_pair = replace_pair.clone()  # cloning the list
    curr_prop = replace_pair.prop_arr.pop(0)

    # if this is the target property that we are to replace
    if not replace_pair.prop_arr:  # if empty
        if not isinstance(data, dict):
            raise AttributeError(
                'The property {} did not belong to a dictionary!'.format(curr_prop))

        # see if target property's value matches
        is_dirty, replacement = replace_pair.matcher(data[curr_prop])
        if is_dirty:
            data[curr_prop] = replacement
            return True
        return False

    value = data[curr_prop]

    # Cursively iterate through the nested properties
    # Note: This doesn't handle list in list. But we don't have that anyway.
    if isinstance(value, list):
        for _ in value:
            is_dirty = bool(_clean_file(_, replace_pair) | is_dirty)
    else:
        is_dirty = bool(_clean_file(value, replace_pair) | is_dirty)
    return is_dirty
