"""
Removes auto-generated clutter.
"""

import os
from os import path
import pprint
import shutil

TARGET_FILES = ['ghostdriver.log']
TARGET_DIRS = ['__pycache__', '.mypy_cache']
EXCLUDE_DIRS = ['py_env']
FOUND_TARGETS = set()


def main() -> None:
    """
    Main function
    """
    print('Cleaning project files...')

    # Get directories
    os.chdir('../')
    curr_path = os.getcwd()
    for root, dirs, files in os.walk(curr_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for dir_ in dirs:
            if dir_ in TARGET_DIRS:
                full_path = path.join(root, dir_)
                FOUND_TARGETS.add(full_path)
        for file in files:
            if file in TARGET_FILES:
                full_path = path.join(root, file)
                FOUND_TARGETS.add(full_path)

    if FOUND_TARGETS:
        pprint.pprint(FOUND_TARGETS)
        key = input('Is this okay? (y/n) ')
        if key.lower() == 'y':
            # Delete targets
            failed_targets = []
            for target in FOUND_TARGETS:
                if path.isdir(target):
                    try:
                        shutil.rmtree(target, ignore_errors=True)
                    except PermissionError:
                        failed_targets.append(target)
                else:
                    os.remove(target)

            # Delete again
            for target in failed_targets:
                shutil.rmtree(target)
            print('\tAll removed')
        else:
            print('No action taken')
    else:
        print('\tNothing found')


if __name__ == '__main__':
    main()
    exit(0)
