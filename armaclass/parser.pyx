import string
import sys

cdef unicode QUOTE = '"'
cdef unicode SEMICOLON = ';'
cdef unicode COLON = ':'
cdef unicode EQUALS = '='
cdef unicode CURLY_OPEN = '{'
cdef unicode CURLY_CLOSE = '}'
cdef unicode SQUARE_OPEN = '['
cdef unicode SQUARE_CLOSE = ']'
cdef unicode COMMA = ','
cdef unicode PLUS = '+'
cdef unicode MINUS = '-'
cdef unicode SLASH = '/'
cdef unicode DOLLAR = '$'
cdef unicode ASTERISK = '*'

cdef unicode NEWLINE = '\n'
cdef unicode TRUE_STR = 'true'
cdef unicode FALSE_STR = 'false'

cdef unicode VALID_NAME_CHAR = string.ascii_letters + string.digits + '_.\\'

cdef long long maxsize = sys.maxsize

class ParseError(RuntimeError):
    pass


cdef class Parser:
    cdef int currentPosition
    cdef unicode raw
    cdef int raw_len
    cdef dict translations

    cdef ensure(self, bint condition, unicode message='Error'):
        if condition:
            return

        raise ParseError('{} at position {}. Before: {}'.format(
            message, self.currentPosition, self.raw[self.currentPosition:self.currentPosition + 50]))

    cdef detectComment(self):
        cdef int indexCommentEnd
        cdef int indexOfLinefeed

        if self.currentPosition >= self.raw_len:
            return

        if self.raw[self.currentPosition] == SLASH:
            if self.currentPosition + 1 >= self.raw_len:
                return

            if self.raw[self.currentPosition + 1] == SLASH:
                # indexOfLinefeed = self.raw.index(NEWLINE, self.currentPosition)
                indexOfLinefeed = self.raw.find(NEWLINE, self.currentPosition)
                if indexOfLinefeed == -1:
                    self.currentPosition = self.raw_len
                else:
                    self.currentPosition = indexOfLinefeed

            elif self.raw[self.currentPosition + 1] == ASTERISK:
                indexCommentEnd = self.raw.find('*/', self.currentPosition)
                self.currentPosition = self.raw_len if indexCommentEnd == -1 else indexCommentEnd + len('*/')

    # cdef detectComment(self):
    #     cdef int indexCommentEnd
    #     cdef int indexOfLinefeed
    #     try:
    #         if self.raw[self.currentPosition] == SLASH:
    #             if self.raw[self.currentPosition + 1] == SLASH:
    #                 try:
    #                     indexOfLinefeed = self.raw.index(NEWLINE, self.currentPosition)
    #                     self.currentPosition = indexOfLinefeed
    #                 except ValueError:
    #                     self.currentPosition = self.raw_len
    #             elif self.raw[self.currentPosition + 1] == ASTERISK:
    #                 indexCommentEnd = self.raw.find('*/', self.currentPosition)
    #                 self.currentPosition = self.raw_len if indexCommentEnd == -1 else indexCommentEnd + len('*/')
    #     except IndexError:
    #         pass

    cdef next(self):
        self.currentPosition += 1
        self.detectComment()
        return self.current()

    cdef nextWithoutCommentDetection(self):
        self.currentPosition += 1
        return self.current()

    cdef unicode current(self):
        # if self.currentPosition >= self.raw_len:
        #     return None
        # return self.raw[self.currentPosition]
        try:
            return self.raw[self.currentPosition]
        except IndexError:
            return None

    cdef bint weHaveADoubleQuote(self):
        cdef unicode double_quote = '""'
        return self.raw[self.currentPosition:self.currentPosition + 2] == double_quote

    cdef bint weHaveAStringLineBreak(self):
        return self.raw[self.currentPosition:self.currentPosition + 6] == '" \\n "'

    cdef forwardToNextQuote(self):
        try:
            self.currentPosition = self.raw.index(QUOTE, self.currentPosition + 1)
        except ValueError:
            self.currentPosition = self.raw_len

    cdef long long indexOfOrMaxSize(self, unicode haystack, unicode needle, int fromPos):
        try:
            return haystack.index(needle, fromPos)
        except ValueError:
            return maxsize

    cdef parseString(self):
        cdef unicode tmp;
        # result = ''
        result = []

        self.ensure(self.current() == QUOTE)
        self.nextWithoutCommentDetection()
        while True:
            if self.weHaveADoubleQuote():
                # result += self.current()
                result.append(self.current())
                self.nextWithoutCommentDetection()
            elif self.weHaveAStringLineBreak():
                # result += '\n'
                result.append('\n')
                self.next()
                self.forwardToNextQuote()
            elif self.current() == QUOTE:
                break
            else:
                tmp = self.current()
                if tmp is None:
                    raise ParseError('Got EOF while parsing a string')

                # result += tmp
                result.append(tmp)

            self.nextWithoutCommentDetection()

        self.ensure(self.current() == QUOTE)
        self.nextWithoutCommentDetection()
        return ''.join(result)
        # return result

    cdef guessExpression(self, unicode s):
        s = s.strip()

        if s[:4].lower() == TRUE_STR:
            return True
        elif s[:5].lower() == FALSE_STR:
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
        posOfExpressionEnd = min(
            self.indexOfOrMaxSize(self.raw, SEMICOLON, self.currentPosition),
            self.indexOfOrMaxSize(self.raw, CURLY_CLOSE, self.currentPosition),
            self.indexOfOrMaxSize(self.raw, COMMA, self.currentPosition)
        )

        expression = self.raw[self.currentPosition:posOfExpressionEnd]
        self.ensure(posOfExpressionEnd != maxsize)
        self.currentPosition = posOfExpressionEnd

        return self.guessExpression(expression)

    cdef parseNonArrayPropertyValue(self):
        cdef unicode current = self.current()
        if current == CURLY_OPEN:
            return self.parseArray()
        elif current == QUOTE:
            return self.parseString()
        elif current == DOLLAR:
            return self.parseTranslationString()
        else:
            return self.parseUnknownExpression()

    cdef bint isValidVarnameChar(self, unicode chr):
        return chr and chr in VALID_NAME_CHAR

    cdef parsePropertyName(self):
        result = self.current()
        while(self.isValidVarnameChar(self.next())):
            result += self.current()

        return result

    cdef parseClassValue(self):
        result = {}

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

        while self.current() != CURLY_CLOSE:
            result.append(self.parseNonArrayPropertyValue())
            self.parseWhitespace()

            if self.current() == COMMA:
                self.next()
                self.parseWhitespace()
            else:
                break

        self.next()
        return result

    cdef void parseWhitespace(self):
        try:
            while self.isWhitespace():
                self.next()
        except IndexError:
            pass

    cdef bint isWhitespace(self):
        return self.raw[self.currentPosition] in ' \t\r\n' or ord(self.raw[self.currentPosition]) < 32

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
        result = ''
        assert self.current() == DOLLAR
        self.next()

        if self.raw[self.currentPosition: self.currentPosition + 3] != 'STR':
            raise ParseError('Invalid translation string beginning')

        while self.current():
            current = self.current()
            if current in (SEMICOLON, COMMA, CURLY_CLOSE):
                break
            else:
                if self.isWhitespace():
                    self.parseWhitespace()
                    break
                else:
                    result += current
            self.nextWithoutCommentDetection()

        if self.current() not in (SEMICOLON, COMMA, CURLY_CLOSE):
            raise ParseError('Syntax error next translation string')

        return self.translateString(result)

    def parse(self, raw, translations):
        self.currentPosition = 0
        self.raw = raw
        self.raw_len = len(raw)
        self.translations = translations if translations else None

        result = {}

        self.detectComment()
        self.parseWhitespace()
        while self.current():
            self.parseProperty(result)
            self.parseWhitespace()

        return result


def parse(raw, *, translations=None):
    p = Parser()
    return p.parse(raw, translations)
