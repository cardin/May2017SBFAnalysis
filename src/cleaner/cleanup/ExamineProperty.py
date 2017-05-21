"""
This module helps create a list of all distinct values of a given property.
"""
import json
import os
from os import path
from typing import Any, Dict, List, Union, Set


def check(json_loc: str, prop_name: str) -> None:
    """
    Extracts the given `prop_name` from all files

    Args:
        json_loc (str): location of JSON folder
        prop_name (str): object-oriented, dot-delimited attribute
    """
    result_list = retrieve(json_loc, prop_name)
    print('\n{}:'.format(prop_name))
    print(result_list)


def retrieve(json_loc: str, prop_name: str) -> Any:
    """
    Extracts the given `prop_name` from all files

    Args:
        json_loc (str): location of JSON folder
        prop_name (str): object-oriented, dot-delimited attribute

    Returns:
        Any: The aggregated property
    """
    prop_arr = prop_name.split('.')

    # Iterate through all files
    dir_results = []
    for dir_ in os.listdir(json_loc):
        abs_dir = path.join(json_loc, dir_)
        dir_results.append(_retrieve_dir(abs_dir, prop_arr))

    # Aggregate results
    result_hash: Set = set()
    for result in dir_results:
        result_hash |= result

    result_list = list(result_hash)
    try:
        result_list.sort()
    except TypeError:
        print('[Suppressed Error] Cannot sort(), contains null')
    return result_list


def _retrieve_dir(abs_dir: str, prop_arr: List[str]) -> Set:
    """
    Runs property retrieval on the files within a directory.
    Suitable for parallelisation.

    Note: Do not multiprocess. Time needed to spin up the process is too slow.

    Args:
        abs_dir (str): location of directory of JSON files
        prop_name (str): object-oriented, dot-delimited attribute

    Returns:
        Any: The aggregated property
    """
    result_hash: Set = set()
    for file in os.listdir(abs_dir):
        abs_file = path.join(abs_dir, file)

        # Open the file
        with open(abs_file) as fstream:
            data = json.load(fstream)

            result = _check_file(data, prop_arr)
            if isinstance(result, set):
                result_hash |= result
            else:
                result_hash.add(result)
    return result_hash


def _check_file(data: Dict, prop_arr: List[str]) -> Union[Set[Any], Any]:
    """
    Digs into a file to pull the desired property out

    Args:
        data (dict): Dictionary (aka JSON)
        prop_arr (list): Array of object-oriented attributes,
                    where the first element is the top-level attribute

    Returns:
        set: Distinct list of values of `prop_name`
    """
    # Removes the first property
    prop_arr = list(prop_arr)  # cloning the list
    curr_prop = prop_arr.pop(0)
    value = data[curr_prop]

    # stop if finished the targeted properties
    if not prop_arr:  # if empty
        vtype = type(value)
        if vtype is list or vtype is dict:
            return str(value)
        return value

    # Cursively iterate through the nested properties
    # Note: This doesn't handle list in list. But we don't have that anyway.
    if isinstance(value, list):
        combi: Set = set()
        for _ in value:
            sub_result = _check_file(_, prop_arr)
            if isinstance(sub_result, set):
                combi |= sub_result
            else:
                combi.add(sub_result)
        return combi
    return _check_file(value, prop_arr)
