"""
Helper utility classes
"""

import os
from os import path
import inspect


def set_project_cwd() -> None:
    """
    Changes current working directory to project level folder
    """
    os.chdir(get_project_path())


def get_project_path() -> str:
    """
    Returns:
        str: Absolute path to project level folder
    """
    curr_dir = os.getcwd()
    while path.basename(curr_dir) != 'May2017SBFAnalysis':
        curr_dir = path.dirname(curr_dir)
    return curr_dir


def get_curr_file_path() -> str:
    """
    Gets the path of the current executing file

    Returns:
        str: Path of current executing file
    """
    frame = inspect.getouterframes(inspect.currentframe())[1][0]
    return path.abspath(inspect.getfile(frame))

def get_curr_folder_path() -> str:
    """
    Gets the path of the current executing file's folder

    Returns:
        str: Path of current executing file's folder
    """
    frame = inspect.getouterframes(inspect.currentframe())[1][0]
    return path.dirname(path.abspath(inspect.getfile(frame)))
