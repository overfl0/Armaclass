# distutils: language=c++

try:
    import cython
except ModuleNotFoundError:
    from .cython_stubs import (cython,
                               PyBytes_GET_SIZE, PyBytes_AS_STRING, PyBytes_AsString, PyUnicode_DecodeUTF8,
                               vector)

if cython.compiled:
    from cython.cimports.cpython import PyBytes_GET_SIZE, PyBytes_AS_STRING, PyBytes_AsString, PyUnicode_DecodeUTF8
    from cython.cimports.libcpp.vector import vector
else:
    from .cython_stubs import (cython,
                               PyBytes_GET_SIZE, PyBytes_AS_STRING, PyBytes_AsString, PyUnicode_DecodeUTF8,
                               vector)

QUOTE = ord('"')
SEMICOLON = ord(';')
COLON = ord(':')
EQUALS = ord('=')
CURLY_OPEN = ord('{')
CURLY_CLOSE = ord('}')
SQUARE_OPEN = ord('[')
SQUARE_CLOSE = ord(']')
COMMA = ord(',')
PLUS = ord('+')
MINUS = ord('-')
SLASH = ord('/')
DOLLAR = ord('$')
ASTERISK = ord('*')
NEWLINE = ord('\n')

NEWLINE_U = b'\n'
END_COMMENT_U = b'*/'
QUOTE_U = b'"'
STR = b'STR'

# VALID_NAME_CHAR = string.ascii_letters + string.digits + '_.\\'


class ParseError(RuntimeError):
    pass


cdef class Parser:
    currentPosition: cython.Py_ssize_t
    input_string: cython.p_char
    input_string_len: cython.Py_ssize_t
    translations: dict

    def ensure(self, condition: cython.bint, message='Error'):
        if condition:
            return

        raise ParseError('{} at position {}. Before: {}'.format(
            message, self.currentPosition, self.input_string[self.currentPosition:self.currentPosition + 50]))

    @cython.exceptval(check=False)
    cdef inline void detectComment(self) noexcept:
        indexCommentEnd: cython.Py_ssize_t
        indexOfLinefeed: cython.Py_ssize_t

        if self.currentPosition >= self.input_string_len:
            return

        if self.input_string[self.currentPosition] == SLASH:
            if self.currentPosition + 1 >= self.input_string_len:
                return

            if self.input_string[self.currentPosition + 1] == SLASH:
                indexOfLinefeed = self.input_string.find(NEWLINE_U, self.currentPosition)
                if indexOfLinefeed == -1:
                    self.currentPosition = self.input_string_len
                else:
                    self.currentPosition = indexOfLinefeed
            elif self.input_string[self.currentPosition + 1] == ASTERISK:
                indexCommentEnd = self.input_string.find(END_COMMENT_U, self.currentPosition)
                self.currentPosition = self.input_string_len if indexCommentEnd == -1 else indexCommentEnd + 2

    @cython.exceptval(check=False)
    cdef inline char next(self) noexcept:
        self.currentPosition += 1
        self.detectComment()
        return self.current()

    @cython.exceptval(check=False)
    cdef inline void nextWithoutCommentDetection(self) noexcept:
        self.currentPosition += 1

    @cython.exceptval(check=False)
    cdef inline char current(self) noexcept:
        if self.currentPosition >= self.input_string_len:
            return -1

        return self.input_string[self.currentPosition]

    @cython.exceptval(check=False)
    cdef inline bint weHaveADoubleQuote(self) noexcept:
        if self.input_string_len >= self.currentPosition + 2 and \
                self.input_string[self.currentPosition] == QUOTE and \
                self.input_string[self.currentPosition + 1] == QUOTE:
            return True
        return False

    @cython.exceptval(check=False)
    cdef inline bint weHaveAStringLineBreak(self) noexcept:
        if (
                self.input_string_len >= self.currentPosition + 6 and
                self.input_string[self.currentPosition] == QUOTE and
                self.input_string[self.currentPosition + 1] == ord(' ') and
                self.input_string[self.currentPosition + 2] == ord('\\') and
                self.input_string[self.currentPosition + 3] == ord('n') and
                self.input_string[self.currentPosition + 4] == ord(' ') and
                self.input_string[self.currentPosition + 5] == QUOTE
        ):
            return True
        return False

    @cython.exceptval(check=False)
    cdef inline void forwardToNextQuote(self) noexcept:
        self.currentPosition = self.input_string.find(QUOTE_U, self.currentPosition + 1)
        if self.currentPosition == -1:
            self.currentPosition = self.input_string_len

    cdef inline unicode parseString(self):
        result: vector[cython.char]
        if not cython.compiled:
            result = vector()
        result.reserve(100)

        self.ensure(self.current() == QUOTE)
        self.nextWithoutCommentDetection()
        while True:
            if self.weHaveADoubleQuote():
                result.push_back(self.current())
                self.nextWithoutCommentDetection()
            elif self.weHaveAStringLineBreak():
                result.push_back(NEWLINE)
                self.next()
                self.forwardToNextQuote()
            elif self.current() == QUOTE:
                break
            else:
                if self.currentPosition >= self.input_string_len:
                    raise ParseError('Got EOF while parsing a string')

                result.push_back(self.current())

            self.nextWithoutCommentDetection()

        self.ensure(self.current() == QUOTE)
        self.nextWithoutCommentDetection()

        return PyUnicode_DecodeUTF8(result.data(), result.size(), 'surrogateescape')

    @cython.exceptval(check=False)
    cdef guessExpression(self, s: cython.bytes) noexcept:
        s_len: cython.Py_ssize_t
        s = s.strip()
        slen = len(s)

        if slen == 4 and s.lower() == b'true':
            return True
        elif slen == 5 and s.lower() == b'false':
            return False
        elif s.startswith(b'0x'):
            return int(s, 16)
        elif b'.' in s:
            try:
                return float(s)
            except ValueError:
                return PyUnicode_DecodeUTF8(PyBytes_AS_STRING(s), PyBytes_GET_SIZE(s), 'surrogateescape')
        else:
            try:
                return int(s)
            except ValueError:
                return PyUnicode_DecodeUTF8(PyBytes_AS_STRING(s), PyBytes_GET_SIZE(s), 'surrogateescape')

    @cython.exceptval(check=False)
    cdef parseUnknownExpression(self) noexcept:
        pos: cython.Py_ssize_t
        c: cython.char

        pos = self.currentPosition
        while True:
            if pos >= self.input_string_len:
                self.ensure(pos < self.input_string_len)  # Just to make it fail

            c = self.input_string[pos]
            if c in b';},':
                break

            pos += 1

        expression = self.input_string[self.currentPosition:pos]
        self.currentPosition = pos

        return self.guessExpression(expression)

    @cython.cfunc
    cdef parseNonArrayPropertyValue(self):
        current: cython.char = self.current()
        if current == CURLY_OPEN:
            return self.parseArray()
        elif current == QUOTE:
            return self.parseString()
        elif current == DOLLAR:
            return self.parseTranslationString()
        else:
            return self.parseUnknownExpression()

    @cython.exceptval(check=False)
    cdef inline bint isValidVarnameChar(self, c: cython.char) noexcept:
        return c in b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.\\'

    cdef bytes parsePropertyName(self):
        start: cython.Py_ssize_t = self.currentPosition
        stop: cython.Py_ssize_t = self.currentPosition + 1

        self.nextWithoutCommentDetection()
        while self.currentPosition < self.input_string_len and self.isValidVarnameChar(self.current()):
            stop += 1
            self.nextWithoutCommentDetection()

        self.detectComment()

        return self.input_string[start:stop]

    cdef parseClassValue(self):
        result: dict = {}

        self.ensure(self.current() == CURLY_OPEN)
        self.next()
        self.parseWhitespace()

        while(self.current() != CURLY_CLOSE):
            self.parseProperty(result)
            self.parseWhitespace()

        self.next()

        return result

    cdef parseArray(self):
        result = []
        self.ensure(self.current() == CURLY_OPEN)
        self.next()
        self.parseWhitespace()

        while self.currentPosition < self.input_string_len and self.current() != CURLY_CLOSE:
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
    cdef inline void parseWhitespace(self) noexcept:
        while self.isWhitespace():
            self.next()

    @cython.exceptval(check=False)
    cdef inline bint isWhitespace(self) noexcept:
        c: cython.char
        if self.input_string_len <= self.currentPosition:
            return False

        c = self.input_string[self.currentPosition]
        return c in b' \t\r\n' or c < 32

    cdef void parseProperty(self, context: dict):
        value = None
        name = self.parsePropertyName()

        self.parseWhitespace()

        if name == b'class':
            name = self.parsePropertyName()
            self.parseWhitespace()

            if self.current() == COLON:
                self.next()
                self.parseWhitespace()
                self.parsePropertyName()
                self.parseWhitespace()

        elif name == b'delete':
            self.parsePropertyName()
            self.parseWhitespace()
            self.ensure(self.current() == SEMICOLON)
            self.next()
            return

        elif name == b'import':
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
                self.currentPosition = self.input_string.find(NEWLINE_U, self.currentPosition)
                if self.currentPosition == -1:
                    self.currentPosition = self.input_string_len

            else:
                raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        else:
            raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        context[PyUnicode_DecodeUTF8(PyBytes_AS_STRING(name), PyBytes_GET_SIZE(name), 'surrogateescape')] = value

        self.parseWhitespace()
        self.ensure(self.current() == SEMICOLON)
        self.next()

    @cython.cfunc
    cdef str translateString(self, txt: str):
        translated: str = self.translations.get(txt)
        if translated is not None:
            return translated
        return txt

    @cython.cfunc
    cdef parseTranslationString(self):
        result: vector[cython.char]
        if not cython.compiled:
            result = vector()
        result.reserve(100)

        assert self.current() == DOLLAR
        self.next()

        if self.input_string[self.currentPosition: self.currentPosition + 3] != STR:
            raise ParseError('Invalid translation string beginning')

        while self.currentPosition < self.input_string_len:
            current: cython.char = self.current()
            if current in b';,}':
                break
            else:
                if self.isWhitespace():
                    self.parseWhitespace()
                    break
                else:
                    result.push_back(current)
            self.nextWithoutCommentDetection()

        if self.currentPosition >= self.input_string_len or self.current() not in b';,}':
            raise ParseError('Syntax error next translation string')

        return self.translateString(PyUnicode_DecodeUTF8(result.data(), result.size(), 'surrogateescape'))

    def parse(self, raw, translations):
        self.currentPosition = 0
        self.input_string = PyBytes_AsString(raw)  # with error checking
        self.input_string_len = len(raw)
        self.translations = translations or {}

        result = {}

        self.detectComment()
        self.parseWhitespace()
        while self.currentPosition < self.input_string_len:
            self.parseProperty(result)
            self.parseWhitespace()

        return result


def parse(raw, *, translations=None):
    p = Parser()
    if not isinstance(raw, bytes):
        return p.parse(raw.encode('utf-8', errors='surrogateescape'), translations)
    return p.parse(raw, translations)
