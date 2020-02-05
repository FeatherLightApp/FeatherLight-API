import os
import sys
import json
from secrets import token_hex



def write_keys(directory):
    with open(os.path.join(directory, 'keys.json'), 'x') as f:
        d = {
            'refresh_secret': token_hex(20),
            'access_secret': token_hex(20),
            'cookie_name': token_hex(10)
        }
        json.dump(d, f, indent=4)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        raise ValueError('Received too many arguments')

    cd = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    write_keys(cd)

