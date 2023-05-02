# distutils: language = c++

from cpython cimport PyUnicode_FromKindAndData, PyUnicode_4BYTE_KIND, PyUnicode_DATA,\
    PyUnicode_KIND, PyUnicode_READ, PyUnicode_1BYTE_KIND, PyUnicode_2BYTE_KIND, PyUnicode_1BYTE_DATA, \
    PyUnicode_2BYTE_DATA, PyUnicode_4BYTE_DATA, PyUnicode_FindChar

cdef extern from *:
    ctypedef unsigned char Py_UCS1  # uint8_t
    ctypedef unsigned short Py_UCS2  # uint16_t

ctypedef fused ucs_character:
    Py_UCS1
    Py_UCS2
    Py_UCS4

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

    cdef ensure(self, bint condition, unicode message='Error'):
        if condition:
            return

        raise ParseError('{} at position {}. Before: {}'.format(
            message, self.currentPosition, self.raw[self.currentPosition:self.currentPosition + 50]))

    @cython.exceptval(check=False)
    cdef void detectComment(self, const ucs_character char_type) noexcept:
        cdef Py_ssize_t indexCommentEnd
        cdef Py_ssize_t indexOfLinefeed

        if self.currentPosition >= self.raw_len:
            return

        if (<ucs_character *>self.very_raw)[self.currentPosition] == SLASH:
            if self.currentPosition + 1 >= self.raw_len:
                return

            if (<ucs_character *>self.very_raw)[self.currentPosition + 1] == SLASH:
                indexOfLinefeed = PyUnicode_FindChar(self.raw, NEWLINE, self.currentPosition, self.raw_len, 1)
                if indexOfLinefeed == -1:
                    self.currentPosition = self.raw_len
                else:
                    self.currentPosition = indexOfLinefeed

            elif (<ucs_character *>self.very_raw)[self.currentPosition + 1] == ASTERISK:
                indexCommentEnd = self.raw.find('*/', self.currentPosition)
                self.currentPosition = self.raw_len if indexCommentEnd == -1 else indexCommentEnd + 2 #+ len('*/')

    @cython.exceptval(check=False)
    cdef Py_UCS4 next(self, const ucs_character char_type) noexcept:
        self.currentPosition += 1
        self.detectComment(char_type)
        return self.current(char_type)

    @cython.exceptval(check=False)
    cdef inline void nextWithoutCommentDetection(self) noexcept:
        self.currentPosition += 1

    @cython.exceptval(check=False)
    cdef Py_UCS4 current(self, const ucs_character char_type) noexcept:
        if self.currentPosition >= self.raw_len:
            return -1

        return (<ucs_character *>self.very_raw)[self.currentPosition]

    @cython.exceptval(check=False)
    cdef bint weHaveADoubleQuote(self, const ucs_character char_type) noexcept:
        if self.raw_len >= self.currentPosition + 2 and \
                (<ucs_character *>self.very_raw)[self.currentPosition] == QUOTE and \
                (<ucs_character *>self.very_raw)[self.currentPosition + 1] == QUOTE:
            return True
        return False

    @cython.exceptval(check=False)
    cdef bint weHaveAStringLineBreak(self, const ucs_character char_type) noexcept:
        if (
            self.raw_len >= self.currentPosition + 6 and
            (<ucs_character *>self.very_raw)[self.currentPosition] == QUOTE and
            (<ucs_character *>self.very_raw)[self.currentPosition + 1] == SPACE and
            (<ucs_character *>self.very_raw)[self.currentPosition + 2] == BACKSLASH and
            (<ucs_character *>self.very_raw)[self.currentPosition + 3] == N and
            (<ucs_character *>self.very_raw)[self.currentPosition + 4] == SPACE and
            (<ucs_character *>self.very_raw)[self.currentPosition + 5] == QUOTE
        ):
            return True
        return False

    cdef void forwardToNextQuote(self, ucs_character char_type) noexcept:
        self.currentPosition = self.raw.find(QUOTE_U, self.currentPosition + 1)
        if self.currentPosition == -1:
            self.currentPosition = self.raw_len


    cdef unicode parseString(self, const ucs_character char_type):
        cdef Py_UCS4 tmp;
        cdef vector[Py_UCS4] result
        result.reserve(100)

        self.ensure(self.current(char_type) == QUOTE)
        self.nextWithoutCommentDetection()
        while True:
            if self.weHaveADoubleQuote(char_type):
                result.push_back(self.current(char_type))
                self.nextWithoutCommentDetection()
            elif self.weHaveAStringLineBreak(char_type):
                result.push_back(NEWLINE)
                self.next(char_type)
                self.forwardToNextQuote(char_type)
            elif self.current(char_type) == QUOTE:
                break
            else:
                tmp = self.current(char_type)
                if tmp == <Py_UCS4>-1:
                    raise ParseError('Got EOF while parsing a string')

                result.push_back(tmp)

            self.nextWithoutCommentDetection()

        self.ensure(self.current(char_type) == QUOTE)
        self.nextWithoutCommentDetection()
        unicode_obj = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, result.data(), result.size())
        return unicode_obj

    cdef guessExpression(self, unicode s):
        cdef Py_ssize_t slen
        s = s.strip()
        slen = len(s)

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

    cdef parseUnknownExpression(self, const ucs_character char_type):
        cdef Py_ssize_t pos
        cdef Py_UCS4 c

        pos = self.currentPosition
        while True:
            if pos >= self.raw_len:
                self.ensure(pos < self.raw_len)  # Just to make it fail

            c = (<ucs_character *> self.very_raw)[pos]
            if c in ';},':
                break

            pos += 1

        expression = self.raw[self.currentPosition:pos]
        self.currentPosition = pos

        return self.guessExpression(expression)

    cdef parseNonArrayPropertyValue(self, const ucs_character char_type):
        cdef Py_UCS4 current = self.current(char_type)
        if current == CURLY_OPEN:
            return self.parseArray(char_type)
        elif current == QUOTE:
            return self.parseString(char_type)
        elif current == DOLLAR:
            return self.parseTranslationString(char_type)
        else:
            return self.parseUnknownExpression(char_type)

    @cython.exceptval(check=False)
    cdef inline bint isValidVarnameChar(self, Py_UCS4 c) noexcept:
        return c != -1 and c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.\\'

    cdef unicode parsePropertyName(self, const ucs_character char_type) noexcept:
        cdef Py_ssize_t start = self.currentPosition
        cdef Py_ssize_t stop = self.currentPosition + 1

        while self.isValidVarnameChar(self.next(char_type)):
            stop += 1

        return self.raw[start:stop]

    cdef parseClassValue(self, const ucs_character char_type):
        cdef dict result = {}

        self.ensure(self.current(char_type) == CURLY_OPEN)
        self.next(char_type)
        self.parseWhitespace(char_type)

        while(self.current(char_type) != CURLY_CLOSE):
            self.parseProperty(char_type, result)
            self.parseWhitespace(char_type)

        self.next(char_type)

        return result

    cdef parseArray(self, const ucs_character char_type):
        cdef list result = []
        self.ensure(self.current(char_type) == CURLY_OPEN)
        self.next(char_type)
        self.parseWhitespace(char_type)

        while self.current(char_type) != -1 and self.current(char_type) != CURLY_CLOSE:
            result.append(self.parseNonArrayPropertyValue(char_type))
            self.parseWhitespace(char_type)

            if self.current(char_type) == COMMA:
                self.next(char_type)
                self.parseWhitespace(char_type)
            else:
                break

        self.next(char_type)
        return result

    @cython.exceptval(check=False)
    cdef void parseWhitespace(self, const ucs_character char_type) noexcept:
        while self.isWhitespace(char_type):
            self.next(char_type)

    @cython.exceptval(check=False)
    cdef bint isWhitespace(self, const ucs_character char_type) noexcept:
        cdef Py_UCS4 c
        if self.raw_len <= self.currentPosition:
            return False

        c = (<ucs_character *>self.very_raw)[self.currentPosition]
        return c in ' \t\r\n' or ord(c) < 32

    cdef void parseProperty(self, const ucs_character char_type, dict context):
        value = None
        name = self.parsePropertyName(char_type)

        self.parseWhitespace(char_type)

        if name == 'class':
            name = self.parsePropertyName(char_type)
            self.parseWhitespace(char_type)

            if self.current(char_type) == COLON:
                self.next(char_type)
                self.parseWhitespace(char_type)
                self.parsePropertyName(char_type)
                self.parseWhitespace(char_type)

        elif name == 'delete':
            self.parsePropertyName(char_type)
            self.parseWhitespace(char_type)
            self.ensure(self.current(char_type) == SEMICOLON)
            self.next(char_type)
            return

        elif name == 'import':
            self.parsePropertyName(char_type)
            self.parseWhitespace(char_type)
            self.ensure(self.current(char_type) == SEMICOLON)
            self.next(char_type)
            return

        current = self.current(char_type)

        if current == SQUARE_OPEN:
            self.ensure(self.next(char_type) == SQUARE_CLOSE)
            self.next(char_type)
            self.parseWhitespace(char_type)

            self.ensure(self.current(char_type) == EQUALS or self.current(char_type) == PLUS)
            if self.current(char_type) == PLUS:
                self.ensure(self.next(char_type) == EQUALS)

            self.next(char_type)
            self.parseWhitespace(char_type)

            value = self.parseArray(char_type)

        elif current == EQUALS:
            self.next(char_type)
            self.parseWhitespace(char_type)
            value = self.parseNonArrayPropertyValue(char_type)

        elif current == CURLY_OPEN:
            value = self.parseClassValue(char_type)

        elif current == SLASH:
            if self.next(char_type) == SLASH:
                try:
                    self.currentPosition = self.raw.index('\n', self.currentPosition)
                except ValueError:
                    self.currentPosition = self.raw_len

            else:
                raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        else:
            raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        context[name] = value

        self.parseWhitespace(char_type)
        self.ensure(self.current(char_type) == SEMICOLON)
        self.next(char_type)

    cdef unicode translateString(self, txt: unicode):
        try:
            return self.translations[txt]
        except KeyError:
            return txt

    cdef parseTranslationString(self, const ucs_character char_type):
        cdef Py_UCS4 current

        result = []
        assert self.current(char_type) == DOLLAR
        self.next(char_type)

        if self.raw[self.currentPosition: self.currentPosition + 3] != 'STR':
            raise ParseError('Invalid translation string beginning')

        while self.current(char_type) != <Py_UCS4>-1:
            current = self.current(char_type)
            if current in (SEMICOLON, COMMA, CURLY_CLOSE):
                break
            else:
                if self.isWhitespace(char_type):
                    self.parseWhitespace(char_type)
                    break
                else:
                    result.append(current)
            self.nextWithoutCommentDetection()

        if self.current(char_type) not in (SEMICOLON, COMMA, CURLY_CLOSE):
            raise ParseError('Syntax error next translation string')

        return self.translateString(''.join(result))

    cdef _parse(self, const ucs_character char_type):
        result = {}
        self.detectComment(char_type)
        self.parseWhitespace(char_type)

        while self.current(char_type) != <Py_UCS4>-1:
            self.parseProperty(char_type, result)
            self.parseWhitespace(char_type)

        return result

    def parse(self, raw, translations):
        self.currentPosition = 0
        self.raw = raw
        self.raw_len = len(raw)
        self.translations = translations if translations else None

        self.very_raw = PyUnicode_DATA(self.raw)
        self.very_raw_kind = PyUnicode_KIND(self.raw)

        if self.very_raw_kind == PyUnicode_1BYTE_KIND:
            return self._parse(<Py_UCS1><Py_UCS4>'a')
        elif self.very_raw_kind == PyUnicode_2BYTE_KIND:
            return self._parse(<Py_UCS2><Py_UCS4>'a')
        elif self.very_raw_kind == PyUnicode_4BYTE_KIND:
            return self._parse(<Py_UCS4>'a')
        else:
            raise RuntimeError('Unsupported unicode kind')


def parse(raw, *, translations=None):
    p = Parser()
    return p.parse(raw, translations)
