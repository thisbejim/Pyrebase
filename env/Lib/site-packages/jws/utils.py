from __future__ import unicode_literals

import base64
import json

import sys
if sys.version < '3':
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes

def to_bytes_2and3(s):
    if type(s) != binary_type:
        s = bytes(s, 'UTF-8')
    return s

def base64url_decode(input):
    input = to_bytes_2and3(input)
    input += b'=' * (4 - (len(input) % 4))
    return base64.urlsafe_b64decode(input)
def base64url_encode(input):
    return base64.urlsafe_b64encode(to_bytes_2and3(input)).replace(b'=', b'')

def to_json(a): return json.dumps(a)
def from_json(a): return json.loads(a)
def to_base64(a): return base64url_encode(a)
def from_base64(a): return base64url_decode(a)
def encode(a): return to_base64(to_json(a))
def decode(a): return from_json(from_base64(a))

#Taken from Django Source Code

def _ord(val):
    if sys.version < '3':
        return ord(val)
    else:
        return val

def constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.

    For the sake of simplicity, this function executes in constant time only
    when the two strings have the same length. It short-circuits when they
    have different lengths.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= _ord(x) ^ _ord(y)
    return result == 0
