"""
This script synchronises all replicas of target files in the solution directory.

Because Python does not allow import beyond top-level package. So there are 2 solutions:
	1) Replicate external dependencies
	2) Use sys.path to import

Option 1 allows us to keep IDE code hints.
The replicas might get a little messy in Git but should be alright.
"""

import os
from os import path
import shutil


def replicate(source: str) -> None:
    """
    Given an absolute filepath, will overwrite any files with the same filename

    Args:
            source (str): The absolute filepath
    """
    source = path.normpath(path.join(os.getcwd(), source))
    filename = path.basename(source)

    for root, _, files in os.walk(os.getcwd(), topdown=True):
        for file in files:
            abs_path = path.join(root, file)
            if abs_path == source:
                continue
            if file == filename:
                print("\tOverwriting " + abs_path)
                shutil.copy(source, abs_path)


def main() -> None:
    """
    Main function
    """
    print('Replicating files...')
    os.chdir('..')

    replicate('src/misc/ProjUtils.py')


if __name__ == '__main__':
    main()
    exit(0)
