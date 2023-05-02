# distutils: language = c++

from cpython cimport PyUnicode_FromKindAndData, PyUnicode_4BYTE_KIND, PyUnicode_DATA,\
    PyUnicode_KIND, PyUnicode_READ, PyUnicode_1BYTE_KIND, PyUnicode_2BYTE_KIND, PyUnicode_1BYTE_DATA, \
    PyUnicode_2BYTE_DATA, PyUnicode_4BYTE_DATA, PyUnicode_FindChar

cdef extern from *:
    ctypedef unsigned char Py_UCS1  # uint8_t
    ctypedef unsigned short Py_UCS2  # uint16_t

cimport cython
from libcpp.vector cimport vector

cdef Py_UCS4 QUOTE = '"'
cdef unicode QUOTE_U = '"'
cdef Py_UCS4 SEMICOLON = ';'
cdef Py_UCS4 COLON = ':'
cdef Py_UCS4 EQUALS = '='
cdef Py_UCS4 CURLY_OPEN = '{'
cdef Py_UCS4 CURLY_CLOSE = '}'
cdef Py_UCS4 SQUARE_OPEN = '['
cdef Py_UCS4 SQUARE_CLOSE = ']'
cdef Py_UCS4 COMMA = ','
cdef Py_UCS4 PLUS = '+'
cdef Py_UCS4 MINUS = '-'
cdef Py_UCS4 SLASH = '/'
cdef Py_UCS4 DOLLAR = '$'
cdef Py_UCS4 ASTERISK = '*'
cdef Py_UCS4 SPACE = ' '
cdef Py_UCS4 BACKSLASH = '\\'
cdef Py_UCS4 N = 'n'

cdef Py_UCS4 NEWLINE = '\n'


class ParseError(RuntimeError):
    pass


cdef class Parser:
    cdef Py_ssize_t currentPosition
    cdef unicode raw
    cdef Py_ssize_t raw_len
    cdef dict translations

    cdef void *very_raw
    cdef int very_raw_kind
    cdef getter

    cdef ensure(self, bint condition, unicode message='Error'):
        if condition:
            return

        raise ParseError('{} at position {}. Before: {}'.format(
            message, self.currentPosition, self.raw[self.currentPosition:self.currentPosition + 50]))

    @cython.exceptval(check=False)
    cdef inline void detectComment(self) noexcept:
        cdef Py_ssize_t indexCommentEnd
        cdef Py_ssize_t indexOfLinefeed

        if self.currentPosition >= self.raw_len:
            return

        # if self.raw[self.currentPosition] == SLASH:
        if PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition) == SLASH:
            if self.currentPosition + 1 >= self.raw_len:
                return

            if PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition + 1) == SLASH:
                # indexOfLinefeed = self.raw.index(NEWLINE, self.currentPosition)
                # indexOfLinefeed = self.raw.find(NEWLINE, self.currentPosition)
                indexOfLinefeed = PyUnicode_FindChar(self.raw, NEWLINE, self.currentPosition, self.raw_len, 1)
                if indexOfLinefeed == -1:
                    self.currentPosition = self.raw_len
                else:
                    self.currentPosition = indexOfLinefeed

            elif PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition + 1) == ASTERISK:
                indexCommentEnd = self.raw.find('*/', self.currentPosition)
                self.currentPosition = self.raw_len if indexCommentEnd == -1 else indexCommentEnd + 2 #+ len('*/')

    @cython.exceptval(check=False)
    cdef inline Py_UCS4 next(self) noexcept:
        self.currentPosition += 1
        self.detectComment()
        return self.current()

    @cython.exceptval(check=False)
    cdef inline void nextWithoutCommentDetection(self) noexcept:
        self.currentPosition += 1

    @cython.exceptval(check=False)
    cdef inline Py_UCS4 current(self) noexcept:
        if self.currentPosition >= self.raw_len:
            return -1

        if self.very_raw_kind == PyUnicode_1BYTE_KIND:
            return (<Py_UCS1 *>self.very_raw)[self.currentPosition]
        if self.very_raw_kind == PyUnicode_2BYTE_KIND:
            return (<Py_UCS2 *> self.very_raw)[self.currentPosition]
        if self.very_raw_kind == PyUnicode_4BYTE_KIND:
            return (<Py_UCS4 *> self.very_raw)[self.currentPosition]
        #
        #
        # return PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition)
        # return self.raw[self.currentPosition]

    @cython.exceptval(check=False)
    cdef inline bint weHaveADoubleQuote(self) noexcept:
        # return self.raw[self.currentPosition:self.currentPosition + 2] == double_quote
        if self.raw_len >= self.currentPosition + 2 and \
                PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition) == QUOTE and \
                PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition + 1) == QUOTE:
            return True
        return False

    @cython.exceptval(check=False)
    cdef bint weHaveAStringLineBreak(self) noexcept:
        if (
            self.raw_len >= self.currentPosition + 6 and
            PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition) == QUOTE and
            PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition + 1) == SPACE and
            PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition + 2) == BACKSLASH and
            PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition + 3) == N and
            PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition + 4) == SPACE and
            PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition + 5) == QUOTE
        ):
            return True
        return False
        #return self.raw[self.currentPosition:self.currentPosition + 6] == '" \\n "'

    cdef void forwardToNextQuote(self) noexcept:
        self.currentPosition = self.raw.find(QUOTE_U, self.currentPosition + 1)
        if self.currentPosition == -1:
            self.currentPosition = self.raw_len


    cdef unicode parseString(self):
        cdef Py_UCS4 tmp;
        cdef vector[Py_UCS4] result
        result.reserve(100)

        self.ensure(self.current() == QUOTE)
        self.nextWithoutCommentDetection()
        while True:
            if self.weHaveADoubleQuote():
                # result += self.current()
                result.push_back(self.current())
                self.nextWithoutCommentDetection()
            elif self.weHaveAStringLineBreak():
                # result += '\n'
                result.push_back(NEWLINE)
                self.next()
                self.forwardToNextQuote()
            elif self.current() == QUOTE:
                break
            else:
                tmp = self.current()
                if tmp == <Py_UCS4>-1:
                    raise ParseError('Got EOF while parsing a string')

                # result += tmp
                result.push_back(tmp)

            self.nextWithoutCommentDetection()

        self.ensure(self.current() == QUOTE)
        self.nextWithoutCommentDetection()
        unicode_obj = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, result.data(), result.size())
        return unicode_obj

    cdef guessExpression(self, unicode s):
        cdef Py_ssize_t slen
        s = s.strip()
        slen = len(s)

        # cdef void *s_raw
        # cdef int s_raw_kind
        #
        # s_raw = PyUnicode_DATA(s)
        # s_raw_kind = PyUnicode_KIND(s)
        #
        # if slen == 4 and \
        #         PyUnicode_READ(s_raw_kind, s_raw, 0) in 'tT' and \
        #         PyUnicode_READ(s_raw_kind, s_raw, 1) in 'rR' and \
        #         PyUnicode_READ(s_raw_kind, s_raw, 2) in 'uU' and \
        #         PyUnicode_READ(s_raw_kind, s_raw, 3) in 'eE':
        #     return True
        # elif slen == 5 and \
        #         PyUnicode_READ(s_raw_kind, s_raw, 0) in 'fF' and \
        #         PyUnicode_READ(s_raw_kind, s_raw, 1) in 'aA' and \
        #         PyUnicode_READ(s_raw_kind, s_raw, 2) in 'lL' and \
        #         PyUnicode_READ(s_raw_kind, s_raw, 3) in 'sS' and \
        #         PyUnicode_READ(s_raw_kind, s_raw, 4) in 'eE':
        #     return False
        if slen == 4 and s.lower() == 'true':
            return True
        elif slen == 5 and s.lower() == 'false':
            return False
        elif s.startswith('0x'):
            return int(s, 16)
        elif '.' in s:
            try:
                return float(s)
            except ValueError:
                return s
        else:
            try:
                return int(s)
            except ValueError:
                return s

    cdef parseUnknownExpression(self):
        cdef Py_ssize_t pos
        cdef Py_UCS4 c

        pos = self.currentPosition
        while True:
            if pos >= self.raw_len:
                self.ensure(pos < self.raw_len)  # Just to make it fail

            c = PyUnicode_READ(self.very_raw_kind, self.very_raw, pos)
            if c in ';},':
                break

            pos += 1

        expression = self.raw[self.currentPosition:pos]
        self.currentPosition = pos

        return self.guessExpression(expression)

    cdef parseNonArrayPropertyValue(self):
        cdef Py_UCS4 current = self.current()
        if current == CURLY_OPEN:
            return self.parseArray()
        elif current == QUOTE:
            return self.parseString()
        elif current == DOLLAR:
            return self.parseTranslationString()
        else:
            return self.parseUnknownExpression()

    @cython.exceptval(check=False)
    cdef inline bint isValidVarnameChar(self, Py_UCS4 c) noexcept:
        return c != -1 and c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.\\'

    cdef unicode parsePropertyName(self) noexcept:
        cdef Py_ssize_t start = self.currentPosition
        cdef Py_ssize_t stop = self.currentPosition + 1

        while self.isValidVarnameChar(self.next()):
            stop += 1

        # return ''.join(result)
        # return PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, result.data(), result.size())
        return self.raw[start:stop]

    cdef parseClassValue(self):
        cdef dict result = {}

        self.ensure(self.current() == CURLY_OPEN)
        self.next()
        self.parseWhitespace()

        while(self.current() != CURLY_CLOSE):
            self.parseProperty(result)
            self.parseWhitespace()

        self.next()

        return result

    cdef parseArray(self):
        cdef list result = []
        self.ensure(self.current() == CURLY_OPEN)
        self.next()
        self.parseWhitespace()

        while self.current() != -1 and self.current() != CURLY_CLOSE:
            result.append(self.parseNonArrayPropertyValue())
            self.parseWhitespace()

            if self.current() == COMMA:
                self.next()
                self.parseWhitespace()
            else:
                break

        self.next()
        return result

    @cython.exceptval(check=False)
    cdef void parseWhitespace(self) noexcept:
        while self.isWhitespace():
            self.next()

    @cython.exceptval(check=False)
    cdef bint isWhitespace(self) noexcept:
        cdef Py_UCS4 c
        if self.raw_len <= self.currentPosition:
            return False

        c = PyUnicode_READ(self.very_raw_kind, self.very_raw, self.currentPosition)
        return c in ' \t\r\n' or ord(c) < 32

    cdef void parseProperty(self, dict context):
        value = None
        name = self.parsePropertyName()

        self.parseWhitespace()

        if name == 'class':
            name = self.parsePropertyName()
            self.parseWhitespace()

            if self.current() == COLON:
                self.next()
                self.parseWhitespace()
                self.parsePropertyName()
                self.parseWhitespace()

        elif name == 'delete':
            self.parsePropertyName()
            self.parseWhitespace()
            self.ensure(self.current() == SEMICOLON)
            self.next()
            return

        elif name == 'import':
            self.parsePropertyName()
            self.parseWhitespace()
            self.ensure(self.current() == SEMICOLON)
            self.next()
            return

        current = self.current()

        if current == SQUARE_OPEN:
            self.ensure(self.next() == SQUARE_CLOSE)
            self.next()
            self.parseWhitespace()

            self.ensure(self.current() == EQUALS or self.current() == PLUS)
            if self.current() == PLUS:
                self.ensure(self.next() == EQUALS)

            self.next()
            self.parseWhitespace()

            value = self.parseArray()

        elif current == EQUALS:
            self.next()
            self.parseWhitespace()
            value = self.parseNonArrayPropertyValue()

        elif current == CURLY_OPEN:
            value = self.parseClassValue()

        elif current == SLASH:
            if self.next() == SLASH:
                try:
                    self.currentPosition = self.raw.index('\n', self.currentPosition)
                except ValueError:
                    self.currentPosition = self.raw_len

            else:
                raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        else:
            raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        context[name] = value

        self.parseWhitespace()
        self.ensure(self.current() == SEMICOLON)
        self.next()

    cdef unicode translateString(self, txt: unicode):
        try:
            return self.translations[txt]
        except KeyError:
            return txt

    cdef parseTranslationString(self):
        cdef Py_UCS4 current

        result = []
        assert self.current() == DOLLAR
        self.next()

        if self.raw[self.currentPosition: self.currentPosition + 3] != 'STR':
            raise ParseError('Invalid translation string beginning')

        while self.current() != <Py_UCS4>-1:
            current = self.current()
            if current in (SEMICOLON, COMMA, CURLY_CLOSE):
                break
            else:
                if self.isWhitespace():
                    self.parseWhitespace()
                    break
                else:
                    result.append(current)
            self.nextWithoutCommentDetection()

        if self.current() not in (SEMICOLON, COMMA, CURLY_CLOSE):
            raise ParseError('Syntax error next translation string')

        return self.translateString(''.join(result))

    def parse(self, raw, translations):
        self.currentPosition = 0
        self.raw = raw
        self.raw_len = len(raw)
        self.translations = translations if translations else None

        self.very_raw = PyUnicode_DATA(self.raw)
        self.very_raw_kind = PyUnicode_KIND(self.raw)

        # if self.very_raw_kind == PyUnicode_1BYTE_KIND:
        #     self.getter = PyUnicode_1BYTE_DATA
        # elif self.very_raw_kind == PyUnicode_2BYTE_KIND:
        #     self.getter = PyUnicode_2BYTE_DATA
        # elif self.very_raw_kind == PyUnicode_4BYTE_KIND:
        #     self.getter = PyUnicode_4BYTE_DATA
        # else:
        #     raise RuntimeError('Unsupported unicode kind')

        result = {}

        self.detectComment()
        self.parseWhitespace()

        while self.current() != <Py_UCS4>-1:
            self.parseProperty(result)
            self.parseWhitespace()

        return result


def parse(raw, *, translations=None):
    p = Parser()
    return p.parse(raw, translations)


# TODO: Try a function pointer for reading the correct unicode data
