import struct

def toHex(number):
    return hex(number)

def byte_list_to_float(byte_list):
    return struct.unpack(">f", byte_list)[0]