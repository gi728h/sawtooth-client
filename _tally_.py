from _init_ import CANDIDATES
import hashlib
import requests # type: ignore
import base64
import cbor # type: ignore
import os

def _sha512(data):
    return hashlib.sha512(data).hexdigest()

def _get_prefix():
    return _sha512('intkey'.encode('utf-8'))[0:6]

def _get_address(name):
    prefix = _get_prefix()
    game_address = _sha512(name.encode('utf-8'))[64:]
    return prefix + game_address

def _fetch_state(address):
    r = requests.get(f"http://{os.getenv("NODE_IP")}:8008/state/{address}")
    return r.json()

def _get_value(name):
    address = _get_address(name)
    result = _fetch_state(address)
    # return decoded_value
    try:
        return cbor.loads(base64.b64decode(result["data"]))[name]
    except Exception as e:
        print(e)
        return None

def _tally():
    result = {}
    for candidate in CANDIDATES:
        result[candidate] = _get_value(candidate)
    return result