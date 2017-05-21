import json
import os
from os import path
import time
from typing import ClassVar, Optional

import requests

import ProjUtils


class OneMapAuth(object):
    """
    Reponsible for logging in to OneMap service
    """
    _ONEMAP_AUTH_API: ClassVar[str] = r'https://developers.onemap.sg/privateapi/auth/post/getToken'
    _AUTH_LOC: ClassVar[str] = 'OneMap.key'
    _TOKEN_LOC: ClassVar[str] = 'OneMapToken.key'

    @classmethod
    def get_token(cls) -> str:
        auth_loc = path.join(ProjUtils.get_curr_folder_path(), cls._AUTH_LOC)
        token_loc = path.join(ProjUtils.get_curr_folder_path(), cls._TOKEN_LOC)

        token = cls._get_old_token(token_loc)
        if not token:
            # load auth
            with open(auth_loc, 'r') as fstream:
                auth = json.load(fstream)

            # submit auth
            headers = {'cache-control': 'no-cache'}
            res = requests.post(cls._ONEMAP_AUTH_API,
                                json=auth, headers=headers)
            token_result = json.loads(res.text)
            if 'access_token' not in token_result:
                raise ConnectionError('Error in authentication!')

            # save auth
            with open(token_loc, 'w') as fstream:
                json.dump(token_result, fstream)
            token = token_result['access_token']
        return token

    @staticmethod
    def _get_old_token(token_loc: str) -> str:
        """
        Gets old token from file if it exists
        """
        token: Optional[str] = None
        if path.exists(token_loc):
            with open(token_loc, 'r') as fstream:
                token_result = json.load(fstream)
                fstream.close()

            # check if expired
            if token_result['expiry_timestamp'] <= time.time() + 600:
                os.remove(token_loc)
            else:
                token = token_result['access_token']
        return token
