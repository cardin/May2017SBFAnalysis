import json
import os
from os import path
import time
from typing import ClassVar, Dict, Optional

import pymongo
from pymongo import MongoClient
from pymongo.database import Database

import ProjUtils


class MongoImporter(object):
    """
    Helper class for connecting to the MongoDB database

    Attributes:
        _database (Database): Reference to the connected database
        _json_loc (str): Relative location (from project) of the JSON files
    """
    _CONNECTION_NAME: ClassVar[str] = 'connection.key'

    _database: Optional[Database]
    _json_loc: str

    def __init__(self, json_loc: str) -> None:
        self._database = self._connect()
        self._json_loc = json_loc

    def run(self) -> None:
        print('------------------------------------------------')
        print('[MongoImporter]')
        curr_time = time.time()
        self._import_data()
        self._create_indices()
        self._close()
        print('\tDone in {:.2f} secs'.format(time.time() - curr_time))
        print('------------------------------------------------')

    @classmethod
    def _connect(cls) -> Database:
        """
        Connects to the MongoDB database

        Returns:
            Database: A reference to the database client
        """
        # load the json
        conn_path = path.join(
            ProjUtils.get_curr_folder_path(), cls._CONNECTION_NAME)
        conn_json: Dict
        with open(conn_path) as fstream:
            conn_json = json.load(fstream)

        # open db connection
        conn_uri = 'mongodb://{}:{}@{}'.format(
            conn_json['user'], conn_json['password'], conn_json['hostname'])
        if conn_json['port']:
            conn_uri = '{}:{}'.format(conn_uri, conn_json['port'])
        conn_uri = '{}/{}'.format(conn_uri, conn_json['database'])
        if conn_json['options']:
            conn_uri = '{}?{}'.format(conn_uri, conn_json['options'])
        client = MongoClient(conn_uri)

        # drop collections if database exist
        # PS: we don't drop database because we will lose user roles
        database = client.get_database(conn_json['database'])
        for name in database.collection_names():
            database.drop_collection(name)
        return database

    def _close(self) -> None:
        """
        Closes the database connection
        """
        if self._database:
            self._database.client.close()
            self._database = None

    def _import_data(self) -> None:
        """
        Imports the JSON files into MongoDB
        """
        curr_time = time.time()

        # iterate through every file
        json_path = path.join(os.getcwd(), self._json_loc)
        for root, _, files in os.walk(json_path):
            for file in files:
                file_path = path.join(root, file)
                file_json: Dict
                with open(file_path) as fstream:
                    file_json = json.load(fstream)

                # load file into MongoDB
                self._database['blocks'].insert_many(file_json['blocks'])
        print('\tImport Data: {:.2f} secs'.format(time.time() - curr_time))

    def _create_indices(self):
        """
        Creates indices for faster querying
        """
        def to_index(keys):
            self._database['blocks'].create_index(keys)

        curr_time = time.time()
        to_index('title')
        to_index([('lat', pymongo.ASCENDING), ('long', pymongo.ASCENDING)])
        to_index('apartments.area')
        to_index('apartments.lease_price_list.price')
        print('\tIndexing {:.2f} secs'.format(time.time() - curr_time))
