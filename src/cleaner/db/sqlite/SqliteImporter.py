import json
import os
from os import path
import sqlite3
from sqlite3 import Connection, Cursor
import time
from typing import ClassVar, Dict, Optional

import ProjUtils


class SqliteImporter(object):
    """
    Helper class to import the data files into SQLite.

    Attributes:
        _conn (Connection): SQL database connection
        _sqlite_loc (str): SQLite database location
        _json_loc (str): JSON files location
        _schema_loc (str): SQLite schema location

        _cached_date_id (int): Latest row id for Day table
        _cached_block_id (int): Latest row id for Block table
        _cached_apt_id (int): Latest row id for Apartment table
    """
    _instantiated: ClassVar[bool] = False

    _conn: Connection
    _sqlite_loc: str
    _json_loc: str
    _schema_loc: str

    _cached_date_id: int
    _cached_block_id: int
    _cached_apt_id: int

    def __init__(self) -> None:
        """
        Constructor
        """
        # Singleton
        if SqliteImporter._instantiated:
            raise ConnectionRefusedError(
                'Close the previous instance of SqliteImporter first')
        SqliteImporter._instantiated = True

        # set paths
        self._sqlite_loc = path.join(
            ProjUtils.get_project_path(), 'data', 'database.sqlite')
        self._json_loc = path.join(
            ProjUtils.get_project_path(), 'data', 'json')
        self._schema_loc = path.join(
            ProjUtils.get_curr_folder_path(), 'schema.sql')

        # cached data
        self._cached_date_id = 0
        self._cached_block_id = 0
        self._cached_apt_id = 0

    def run(self) -> None:
        """
        Begins importing the data into the database
        """
        print('------------------------------------------------')
        print('[SqliteImporter]')
        curr_time = time.time()
        self._create_db()

        # Iterate through towns
        town_paths = [path.join(self._json_loc, d) for d in os.listdir(
            self._json_loc) if path.isdir(path.join(self._json_loc, d))]
        for town_path in town_paths:
            self._import_town(town_path)
        print('\tDone in {:.2f} secs'.format(time.time() - curr_time))
        print('------------------------------------------------')

    def close(self) -> None:
        """
        Closes the database connection
        """
        self._conn.close()
        self._conn = None

    def _create_db(self) -> None:
        """
        Creates the database
        """
        # Creates database file if does not exist
        if path.exists(self._sqlite_loc):
            os.remove(self._sqlite_loc)

        # Connect
        self._conn = sqlite3.connect(self._sqlite_loc)  # type: Connection

        # Create the schema
        with open(self._schema_loc, 'r') as fstream:
            schema_sql = fstream.read()
        self._conn.executescript(schema_sql)
        self._conn.commit()

    def _import_town(self, town_path: str) -> None:
        """
        Creates town based on given town directory path

        Args:
            town_path (str): absolute path to a town directory
        """
        cursor = self._conn.cursor()

        # Iterate through flat types
        flat_type_paths = [path.join(town_path, t)
                           for t in os.listdir(town_path)]
        for flat_type_path in flat_type_paths:

            # Open doc
            with open(flat_type_path, 'r') as fstream:
                root = json.load(fstream)

            # Iterate through blocks
            for block_dict in root['blocks']:
                self._import_block(cursor, block_dict)

        cursor.connection.commit()

    def _import_block(self, cursor: Cursor, block_dict: Dict) -> None:
        """
        Creates block based on given block dictionary object

        Args:
            cursor (Cursor): cursor to the database connection
            block_dict (Dict): Block dictionary
        """

        # Insert dates
        pcd_id = self._import_dates(cursor, block_dict['pcd_date'])
        dpd_id = self._import_dates(cursor, block_dict['dpd_date'])
        lcd_id = self._import_dates(cursor, block_dict['lcd_date'])

        # Insert block's fields
        town = block_dict['town']
        title = block_dict['title']
        flat_type = block_dict['flat_type']
        block_num = block_dict['block_code']['block_num']
        street = block_dict['street']
        postal = int(block_dict['postal'])
        lat = float(block_dict['lat'])
        lng = float(block_dict['long'])
        quota_m = int(block_dict['quota_malay'])
        quota_c = int(block_dict['quota_chinese'])
        quota_o = int(block_dict['quota_other'])
        self._cached_block_id += 1
        try:
            cursor.execute('INSERT INTO Block VALUES \
                            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           (town, title, self._cached_block_id,
                            flat_type, block_num, street, postal,
                            lat, lng, pcd_id, dpd_id, lcd_id,
                            quota_m, quota_c, quota_o))
        except Exception as expt:
            raise expt

        # Insert Apartments
        for apartment in block_dict['apartments']:
            floor = int(apartment['floor'])
            unit = apartment['unit']
            area = int(apartment['area'])
            repurchased = bool(apartment['is_repurchased'])
            self._cached_apt_id += 1
            cursor.execute('INSERT INTO Apartment VALUES (?,?,?,?,?,?)',
                           (self._cached_block_id, self._cached_apt_id,
                            floor, unit, area, repurchased))

            # Insert Lease_Price
            for lease_price in apartment['lease_price_list']:
                lease = int(lease_price['lease'])
                price = int(lease_price['price'])
                cursor.execute('INSERT INTO Lease_Price VALUES (?,?,?)',
                               (self._cached_apt_id, lease, price))

    def _import_dates(self, cursor: Cursor, date_dict: Optional[dict]) -> Optional[int]:
        """
        Stores a date into the database, returning the date identifier

        Args:
            cursor (Cursor): cursor to the database connection
            date_dict (dict): A dictionary representing dates

        Returns:
            Optional[int]: Either None if no date, or the identifier to the row in the Day table.
        """
        if not date_dict:
            return None

        self._cached_date_id += 1
        cursor.execute('INSERT INTO Day (day_id, year, month, day, quarter, months_since) \
                        VALUES (?,?,?,?,?,?)',
                       (self._cached_date_id,
                        date_dict['year'],
                        date_dict['month'],
                        date_dict['day'],
                        date_dict['quarter'],
                        date_dict['months_since']))
        return self._cached_date_id
