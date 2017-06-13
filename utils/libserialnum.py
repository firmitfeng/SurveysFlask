# -*- coding: utf-8 -*-  

import binascii
import time
from datetime import datetime

def computeCRC32(str1, plus=None):
    if plus is None:
        return binascii.crc32(str1) & 0xffffffff
    else:
        return binascii.crc32(str1, plus) & 0xffffffff


def encodeSerialNum(str1):
    ts_hex = (hex(int(time.time()))[2:]).upper()
    crc32 = (hex(computeCRC32(str1))[2:]).upper() 
    return ts_hex+crc32


def decodeSerialNum(sn):
    ts = int(sn[0:8], 16)
    crc32 = int(sn[8:], 16)
    return ({'crc32': crc32}, {'timestamp':ts})

if __name__ == "__main__":

    print encodeSerialNum('adfasfasf')
    
    print decodeSerialNum(encodeSerialNum('adfasfasf'))
