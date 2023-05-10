from . import Shadow as cython

PyUnicode_4BYTE_KIND = None
cython.bytes = bytes

def PyBytes_AsString(b):
    return b


def PyBytes_AS_STRING(b):
    return b


def PyBytes_GET_SIZE(b):
    return len(b)


def PyUnicode_DecodeUTF8(data, len, errors):
    return data.decode('utf-8', errors=errors)


class vector:
    def __init__(self):
        self._data = []

    def push_back(self, elem):
        self._data.append(elem)

    def data(self):
        return bytes(self._data)

    def size(self):
        return len(self._data)

    def reserve(self, x):
        pass
