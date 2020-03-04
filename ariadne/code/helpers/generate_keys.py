"""
simple script for gnerating the key file for JWT secrets used by the API

Usage:
python generate_keys.py -> keys.json in cd
python generate_keys.py /some/dir -> keys.json in /some/dir
"""

import os
import sys
import json
from secrets import token_hex


def write_keys(directory: str):
    """generates random keys and writes them to directory"""
    with open(os.path.join(directory, 'keys.json'), 'x') as file:
        data = {
            'refresh_secret': token_hex(20),
            'access_secret': token_hex(20),
            'cookie_name': token_hex(10)
        }
        json.dump(data, file, indent=4)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        raise ValueError('Received too many arguments')

    CURDIR = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    write_keys(CURDIR)
