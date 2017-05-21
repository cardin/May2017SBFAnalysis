"""
This script performs functions related to static analysis.
* Auto-formatting
* Type checking
"""
import os
from os import path
import subprocess
from typing import List

SRC_LOCATION = "../src/"

def detect_projects() -> List[str]:
    """
    Detects projects

    Returns:
        List[str]: List of project names
    """
    dirs = next(os.walk(SRC_LOCATION, topdown=True))[1]

    # remove hidden directories
    proj_dirs = [_ for _ in dirs if _[0] is not '.']
    return proj_dirs

def menu_choice(proj_dirs: List[str]) -> str:
    """
    Presents a menu choice to user on which project to check

    Args:
        proj_dirs (List[str]): List of project names
    Returns:
        str: The project name chosen. If user wishes to terminate, the script exits immediately
    """
    for i, proj_dir in enumerate(proj_dirs):
        print('\t{}. {}'.format(i+1, proj_dir))
    user_input = input('\tSelect a project [-1 to quit]: ')

    # Parse input
    if str.isdigit(user_input):
        proj_i = int(user_input) - 1
        if proj_i in list(range(len(proj_dirs))):
            return proj_dirs[proj_i]
    print("\tClosing")
    exit(0)


def autoformat(abs_proj_path: str) -> None:
    """
    Runs auto-formatting on given project path

    Args:
        abs_proj_path (str): Absolute project path
    """
    command = 'autopep8 -i -r {}'.format(abs_proj_path)
    print('\t\t' + command)
    subprocess.run(command, shell=True)


def type_check(abs_proj_path: str) -> None:
    """
    Runs static type checking on given project path

    Args:
        abs_proj_path (str): Absolute project path
    """
    proj_name = path.basename(abs_proj_path)

    # Change working dir, as mypy isn't very flexible
    orig_cwd = path.abspath(os.getcwd())
    os.chdir(SRC_LOCATION)

    # Prepare mypy.ini
    with open('mypy.ini', 'r') as fstream:
        config = fstream.readlines()
    for i, line in enumerate(config):
        if 'mypy_path = ' in line:
            if proj_name not in line:
                config[i] = '{}, {}\n'.format(line.strip(), proj_name)
    with open('mypy.ini', 'w') as fstream:
        fstream.writelines(config)

    # Run
    command = 'mypy -p {}'.format(path.basename(abs_proj_path))
    print('\t\t' + command)
    subprocess.run(command, shell=True)
    os.chdir(orig_cwd)


def main() -> None:
    """
    Main function
    """
    print('Static Analysis...')

    proj_dirs = detect_projects()
    while True:
        proj_name = menu_choice(proj_dirs)
        full_path = path.abspath(path.join(SRC_LOCATION, proj_name))

        autoformat(full_path)
        type_check(full_path)
        print("\t\tDone!")

if __name__ == '__main__':
    main()
    exit(0)
