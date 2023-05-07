try:
    import cython
except ModuleNotFoundError:
    from .cython_stubs import (cython,
                               PyUnicode_FromKindAndData, PyUnicode_4BYTE_KIND, PyUnicode_DATA,
                               PyUnicode_KIND, PyUnicode_READ,
                               vector)

if cython.compiled:
    from cython.cimports.cpython import (PyUnicode_FromKindAndData, PyUnicode_4BYTE_KIND, PyUnicode_DATA,
                                         PyUnicode_KIND, PyUnicode_READ)
    from cython.cimports.libcpp.vector import vector
else:
    from .cython_stubs import (cython,
                               PyUnicode_FromKindAndData, PyUnicode_4BYTE_KIND, PyUnicode_DATA,
                               PyUnicode_KIND, PyUnicode_READ,
                               vector)

# QUOTE: cython.Py_UCS4 = '"'
# SEMICOLON: cython.Py_UCS4 = ';'
# COLON = ':'
# EQUALS = '='
# CURLY_OPEN = '{'
# CURLY_CLOSE: cython.Py_UCS4 = '}'
# SQUARE_OPEN = '['
# SQUARE_CLOSE = ']'
# COMMA: cython.Py_UCS4 = ','
# PLUS = '+'
# MINUS = '-'
# SLASH: cython.Py_UCS4 = '/'
# DOLLAR = '$'
# ASTERISK = '*'
#
# VALID_NAME_CHAR = string.ascii_letters + string.digits + '_.\\'


class ParseError(RuntimeError):
    pass


@cython.cclass
class Parser:
    currentPosition: cython.Py_ssize_t
    input_string: cython.unicode
    input_string_len: cython.Py_ssize_t
    translations: dict

    data: cython.p_void
    data_kind: cython.int

    @cython.cfunc
    def ensure(self, condition: cython.bint, message='Error'):
        if condition:
            return

        raise ParseError('{} at position {}. Before: {}'.format(
            message, self.currentPosition, self.input_string[self.currentPosition:self.currentPosition + 50]))

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def detectComment(self) -> cython.void:
        indexCommentEnd: cython.Py_ssize_t
        indexOfLinefeed: cython.Py_ssize_t

        if self.currentPosition >= self.input_string_len:
            return

        if PyUnicode_READ(self.data_kind, self.data, self.currentPosition) == '/':
            if self.currentPosition + 1 >= self.input_string_len:
                return

            if PyUnicode_READ(self.data_kind, self.data, self.currentPosition + 1) == '/':
                indexOfLinefeed = self.input_string.find('\n', self.currentPosition)
                if indexOfLinefeed == -1:
                    self.currentPosition = self.input_string_len
                else:
                    self.currentPosition = indexOfLinefeed
            elif PyUnicode_READ(self.data_kind, self.data, self.currentPosition + 1) == '*':
                indexCommentEnd = self.input_string.find('*/', self.currentPosition)
                self.currentPosition = self.input_string_len if indexCommentEnd == -1 else indexCommentEnd + 2

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def next(self) -> cython.Py_UCS4:
        self.currentPosition += 1
        self.detectComment()
        return self.current()

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def nextWithoutCommentDetection(self) -> cython.void:
        self.currentPosition += 1

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def current(self) -> cython.Py_UCS4:
        if self.currentPosition >= self.input_string_len:
            return -1

        return PyUnicode_READ(self.data_kind, self.data, self.currentPosition)

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def weHaveADoubleQuote(self) -> cython.bint:
        if self.input_string_len >= self.currentPosition + 2 and \
                PyUnicode_READ(self.data_kind, self.data, self.currentPosition) == '"' and \
                PyUnicode_READ(self.data_kind, self.data, self.currentPosition + 1) == '"':
            return True
        return False

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def weHaveAStringLineBreak(self) -> cython.bint:
        if (
                self.input_string_len >= self.currentPosition + 6 and
                PyUnicode_READ(self.data_kind, self.data, self.currentPosition) == '"' and
                PyUnicode_READ(self.data_kind, self.data, self.currentPosition + 1) == ' ' and
                PyUnicode_READ(self.data_kind, self.data, self.currentPosition + 2) == '\\' and
                PyUnicode_READ(self.data_kind, self.data, self.currentPosition + 3) == 'n' and
                PyUnicode_READ(self.data_kind, self.data, self.currentPosition + 4) == ' ' and
                PyUnicode_READ(self.data_kind, self.data, self.currentPosition + 5) == '"'
        ):
            return True
        return False

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def forwardToNextQuote(self) -> cython.void:
        self.currentPosition = self.input_string.find('"', self.currentPosition + 1)
        if self.currentPosition == -1:
            self.currentPosition = self.input_string_len

    @cython.cfunc
    @cython.inline
    def parseString(self) -> cython.unicode:
        result: vector[cython.Py_UCS4]# = vector[cython.Py_UCS4]()
        if not cython.compiled:
            result = vector()
        result.reserve(100)

        self.ensure(self.current() == '"')
        self.nextWithoutCommentDetection()
        while True:
            if self.weHaveADoubleQuote():
                result.push_back(self.current())
                self.nextWithoutCommentDetection()
            elif self.weHaveAStringLineBreak():
                result.push_back('\n')
                self.next()
                self.forwardToNextQuote()
            elif self.current() == cython.cast(cython.Py_UCS4, '"'):
                break
            else:
                tmp: cython.Py_UCS4 = self.current()
                if tmp == cython.cast(cython.Py_UCS4, -1):
                    raise ParseError('Got EOF while parsing a string')

                result.push_back(self.current())

            self.nextWithoutCommentDetection()

        self.ensure(self.current() == '"')
        self.nextWithoutCommentDetection()
        unicode_obj = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND, result.data(), result.size())
        return unicode_obj

    @cython.cfunc
    @cython.exceptval(check=False)
    def guessExpression(self, s: cython.unicode):
        s_len: cython.Py_ssize_t
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

    @cython.cfunc
    @cython.exceptval(check=False)
    def parseUnknownExpression(self):
        pos: cython.Py_ssize_t
        c: cython.Py_UCS4

        pos = self.currentPosition
        while True:
            if pos >= self.input_string_len:
                self.ensure(pos < self.input_string_len)  # Just to make it fail

            c = PyUnicode_READ(self.data_kind, self.data, pos)
            if c in ';},':
                break

            pos += 1

        expression = self.input_string[self.currentPosition:pos]
        self.currentPosition = pos

        return self.guessExpression(expression)

    @cython.cfunc
    def parseNonArrayPropertyValue(self):
        current: cython.Py_UCS4 = self.current()
        if current == '{':
            return self.parseArray()
        elif current == '"':
            return self.parseString()
        elif current == '$':
            return self.parseTranslationString()
        else:
            return self.parseUnknownExpression()

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def isValidVarnameChar(self, c: cython.Py_UCS4) -> cython.bint:
        return c != cython.cast(cython.Py_UCS4, -1) and c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.\\'

    @cython.cfunc
    def parsePropertyName(self) -> cython.unicode:
        start: cython.Py_ssize_t = self.currentPosition
        stop: cython.Py_ssize_t = self.currentPosition + 1

        while self.isValidVarnameChar(self.next()):
            stop += 1

        return self.input_string[start:stop]

    @cython.cfunc
    def parseClassValue(self):
        result: dict = {}

        self.ensure(self.current() == '{')
        self.next()
        self.parseWhitespace()

        while(self.current() != '}'):
            self.parseProperty(result)
            self.parseWhitespace()

        self.next()

        return result

    @cython.cfunc
    def parseArray(self):
        result = []
        self.ensure(self.current() == '{')
        self.next()
        self.parseWhitespace()

        while self.current() != cython.cast(cython.Py_UCS4, -1) and self.current() != '}':
            result.append(self.parseNonArrayPropertyValue())
            self.parseWhitespace()

            if self.current() == ',':
                self.next()
                self.parseWhitespace()
            else:
                break

        self.next()
        return result

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def parseWhitespace(self) -> cython.void:
        while self.isWhitespace():
            self.next()

    @cython.cfunc
    @cython.inline
    @cython.exceptval(check=False)
    def isWhitespace(self) -> cython.bint:
        c: cython.Py_UCS4
        if self.input_string_len <= self.currentPosition:
            return False

        c = PyUnicode_READ(self.data_kind, self.data, self.currentPosition)
        return c in ' \t\r\n' or ord(c) < 32

    @cython.cfunc
    def parseProperty(self, context: dict) -> cython.void:
        value = None
        name = self.parsePropertyName()

        self.parseWhitespace()

        if name == 'class':
            name = self.parsePropertyName()
            self.parseWhitespace()

            if self.current() == ':':
                self.next()
                self.parseWhitespace()
                self.parsePropertyName()
                self.parseWhitespace()

        elif name == 'delete':
            self.parsePropertyName()
            self.parseWhitespace()
            self.ensure(self.current() == ';')
            self.next()
            return

        elif name == 'import':
            self.parsePropertyName()
            self.parseWhitespace()
            self.ensure(self.current() == ';')
            self.next()
            return

        current = self.current()

        if current == '[':
            self.ensure(self.next() == ']')
            self.next()
            self.parseWhitespace()

            self.ensure(self.current() == '=' or self.current() == '+')
            if self.current() == '+':
                self.ensure(self.next() == '=')

            self.next()
            self.parseWhitespace()

            value = self.parseArray()

        elif current == '=':
            self.next()
            self.parseWhitespace()
            value = self.parseNonArrayPropertyValue()

        elif current == '{':
            value = self.parseClassValue()

        elif current == '/':
            if self.next() == '/':
                self.currentPosition = self.input_string.find('\n', self.currentPosition)
                if self.currentPosition == -1:
                    self.currentPosition = self.input_string_len

            else:
                raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        else:
            raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        context[name] = value

        self.parseWhitespace()
        self.ensure(self.current() == ';')
        self.next()

    @cython.cfunc
    def translateString(self, txt: str) -> str:
        translated: str = self.translations.get(txt)
        if translated is not None:
            return translated
        return txt

    @cython.cfunc
    def parseTranslationString(self):
        result = []
        assert self.current() == '$'
        self.next()

        if self.input_string[self.currentPosition: self.currentPosition + 3] != 'STR':
            raise ParseError('Invalid translation string beginning')

        while self.current() != cython.cast(cython.Py_UCS4, -1):
            current: cython.Py_UCS4 = self.current()
            if current in ';,}':
                break
            else:
                if self.isWhitespace():
                    self.parseWhitespace()
                    break
                else:
                    result.append(current)
            self.nextWithoutCommentDetection()

        if self.current() == cython.cast(cython.Py_UCS4, -1) or self.current() not in ';,}':
            raise ParseError('Syntax error next translation string')

        return self.translateString(''.join(result))

    def parse(self, raw, translations):
        self.currentPosition = 0
        self.input_string = raw
        self.input_string_len = len(raw)
        self.translations = translations or {}

        self.data = PyUnicode_DATA(self.input_string)
        self.data_kind = PyUnicode_KIND(self.input_string)

        result = {}

        self.detectComment()
        self.parseWhitespace()
        while self.current() != cython.cast(cython.Py_UCS4, -1):
            self.parseProperty(result)
            self.parseWhitespace()

        return result


def parse(raw, *, translations=None):
    p = Parser()
    return p.parse(raw, translations)
