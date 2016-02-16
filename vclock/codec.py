from base64 import b64encode, b64decode
import struct


class ArrayCodec(object):
    """
    This is a default encoding to pack the data. Designed for best storage in ascii.
    You can use a custom encoder for eg. larger data sizes, more felxibility, etc.
    Currently, this handles arrays with no keys, and max 2**8 ids and 2**24 counts
    """
    COUNT_BYTES = 4

    def encode_count(self, big):
        """This encodes a large integer < 2*24 ~= 16 million, into 4 ascii characters"""
        binary = struct.pack(">I", big)
        assert binary[0] == b'\x00'
        binary = binary[1:]
        return b64encode(binary)

    def decode_count(self, ascii):
        """This decodes an integer encoded by encode_counter"""
        binary = b'\x00' + b64decode(ascii)
        big = struct.unpack(">I", binary)[0]
        return big

    def encode_vector(self, vector):
        """Encodes a vector array as a string"""
        return b''.join(self.encode_count(x) for x in vector)

    def decode_vector(self, line):
        """Decodes a vector string into a generator (wrap in list() to instantiate)"""
        n = self.COUNT_BYTES
        return (self.decode_count(line[i:i+n]) for i in range(0, len(line), n))


class DictCodec(ArrayCodec):
    """
    This is a more flexible codec than ArrayCodec, designed to handle a vector that consists
    of key-value pairs (int -> int). It will be somewhat larger when most actors participate,
    but the gain is that when most actors do not touch the item, the clock is much smaller.
    """
    COUNT_BYTES = 6

    def __init__(self, int_keys=True):
        self.int_keys = int_keys

    def encode_key(self, small):
        """This encodes a number from 0 - 255 into two ascii characters"""
        if self.int_keys:
            return b"{:02X}".format(small).upper()
        elif hasattr(small, 'encode'):
            return small.encode('utf-8')
        else:
            return small

    def decode_key(self, ascii):
        if self.int_keys:
            return int(ascii, 16)
        elif hasattr(ascii, 'decode'):
            return ascii.decode('utf-8')
        else:
            return ascii

    def encode_vector(self, vector):
        """Encodes a vector array as a string"""
        result = b''
        for key, value in sorted(vector.items(), reverse=True):
            result += self.encode_key(key) + self.encode_count(value)
        return result

    def decode_vector(self, line):
        """Decodes a vector string into a generator (wrap in list() to instantiate)"""
        n = self.COUNT_BYTES
        result = {}
        for i in range(0, len(line), n):
            ekey, eval = line[i:i+2], line[i+2:i+n]
            result[self.decode_key(ekey)] = self.decode_count(eval)
        return result

