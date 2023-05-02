# distutils: language = c++

from cpython cimport PyUnicode_4BYTE_KIND, PyUnicode_KIND, PyUnicode_1BYTE_KIND, PyUnicode_2BYTE_KIND

from .parser_ucs1 import Parser_UCS1
from .parser_ucs2 import Parser_UCS2
from .parser_ucs4 import Parser_UCS4

cdef class Parser:
    def parse(self, unicode raw, translations):
        raw_kind = PyUnicode_KIND(raw)

        if raw_kind == PyUnicode_1BYTE_KIND:
            parser = Parser_UCS1()
        elif raw_kind == PyUnicode_2BYTE_KIND:
            parser = Parser_UCS2()
        elif raw_kind == PyUnicode_4BYTE_KIND:
            parser = Parser_UCS4()
        else:
            raise RuntimeError('Unsupported unicode kind')

        return parser.parse(raw, translations)


def parse(raw, *, translations=None):
    p = Parser()
    return p.parse(raw, translations)
