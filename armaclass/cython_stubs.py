from . import Shadow as cython

cython.dict = dict
PyUnicode_4BYTE_KIND = None
cython.cast = lambda type_, value: value


def PyUnicode_KIND(data):
    return None


def PyUnicode_FromKindAndData(kind, data, size):
    return data[:size]


def PyUnicode_READ(kind, data, pos):
    return data[pos]


def PyUnicode_DATA(data):
    return data


class vector:
    def __init__(self):
        self._data = []

    def push_back(self, elem):
        self._data.append(elem)

    def data(self):
        return ''.join(self._data)

    def size(self):
        return len(self._data)

    def reserve(self, x):
        pass
