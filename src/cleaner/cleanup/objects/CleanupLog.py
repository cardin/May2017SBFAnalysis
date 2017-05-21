from datetime import datetime
import json
from os import path


class CleanupLog(object):
    """
    Helps log down the completion status of a cleanup process
    """
    @staticmethod
    def has_done(name: str, log_loc: str) -> bool:
        """
        Checks if the given cleanup process has been done before

        Args:
            name (str): Name of the cleanup process
            log_loc (str): Location of the log file

        Returns:
            bool: True if the process has been done before
        """
        if not path.exists(log_loc):
            return False
        with open(log_loc, 'r') as fstream:
            log = json.load(fstream)
            fstream.close()
            return name in log

    @staticmethod
    def log_done(name: str, log_loc: str) -> None:
        """
        Logs that the given cleanup process is done

        Args:
            name (str): Name of the cleanup process
            log_loc (str): Location of the log file
        """
        if path.exists(log_loc):
            with open(log_loc, 'r+') as fstream:
                log = json.load(fstream)
                log[name] = str(datetime.now())

                fstream.seek(0)
                json.dump(log, fstream, indent=4)
                fstream.close()
        else:
            with open(log_loc, 'w') as fstream:
                log = {name: str(datetime.now())}
                json.dump(log, fstream, indent=4)
                fstream.close()
