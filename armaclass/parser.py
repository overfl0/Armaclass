import string
import sys

from collections import OrderedDict

QUOTE = '"'
SEMICOLON = ';'
EQUALS = '='
CURLY_OPEN = '{'
CURLY_CLOSE = '}'
SQUARE_OPEN = '['
SQUARE_CLOSE = ']'
COMMA = ','
PLUS = '+'
MINUS = '-'
SLASH = '/'
DOLLAR = '$'
ASTERISK = '*'

VALID_NAME_CHAR = string.ascii_letters + string.digits + '_.\\'


class ParseError(RuntimeError):
    pass


class Parser:
    def ensure(self, condition, message='Error'):
        if condition:
            return

        raise ParseError('{} at position {}. Before: {}'.format(
            message, self.currentPosition, self.raw[self.currentPosition:self.currentPosition + 50]))

    def detectComment(self):
        try:
            if self.raw[self.currentPosition] == SLASH:
                if self.raw[self.currentPosition + 1] == SLASH:
                    try:
                        indexOfLinefeed = self.raw.index('\n', self.currentPosition)
                        self.currentPosition = indexOfLinefeed
                    except ValueError:
                        self.currentPosition = len(self.raw)
                elif self.raw[self.currentPosition + 1] == ASTERISK:
                    indexCommentEnd = self.raw.find('*/', self.currentPosition)
                    self.currentPosition = len(self.raw) if indexCommentEnd == -1 else indexCommentEnd + len('*/')
        except IndexError:
            pass

    def next(self):
        self.currentPosition += 1
        self.detectComment()
        return self.current()

    def nextWithoutCommentDetection(self):
        self.currentPosition += 1
        return self.current()

    def current(self):
        try:
            return self.raw[self.currentPosition]
        except IndexError:
            return None

    def weHaveADoubleQuote(self):
        return self.raw[self.currentPosition:self.currentPosition + 2] == '""'

    def weHaveAStringLineBreak(self):
        return self.raw[self.currentPosition:self.currentPosition + 6] == '" \\n "'

    def forwardToNextQuote(self):
        try:
            self.currentPosition = self.raw.index(QUOTE, self.currentPosition + 1)
        except ValueError:
            self.currentPosition = len(self.raw)

    def indexOfOrMaxSize(self, haystack, needle, fromPos):
        try:
            return haystack.index(needle, fromPos)
        except ValueError:
            return sys.maxsize

    def parseString(self):
        result = ''
        self.ensure(self.current() == QUOTE)
        self.nextWithoutCommentDetection()
        while True:
            if self.weHaveADoubleQuote():
                result += self.current()
                self.nextWithoutCommentDetection()
            elif self.weHaveAStringLineBreak():
                result += '\n'
                self.next()
                self.forwardToNextQuote()
            elif self.current() == QUOTE:
                break
            else:
                try:
                    result += self.current()
                except TypeError:
                    if self.current() is None:
                        raise ParseError('Got EOF while parsing a string')
                    raise

            self.nextWithoutCommentDetection()

        self.ensure(self.current() == QUOTE)
        self.nextWithoutCommentDetection()
        return result

    def guessExpression(self, s):
        s = s.strip()

        if s[:4].lower() == 'true':
            return True
        elif s[:5].lower() == 'false':
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

    def parseUnknownExpression(self):
        posOfExpressionEnd = min(
            self.indexOfOrMaxSize(self.raw, SEMICOLON, self.currentPosition),
            self.indexOfOrMaxSize(self.raw, CURLY_CLOSE, self.currentPosition),
            self.indexOfOrMaxSize(self.raw, COMMA, self.currentPosition)
        )

        expression = self.raw[self.currentPosition:posOfExpressionEnd]
        self.ensure(posOfExpressionEnd != sys.maxsize)
        self.currentPosition = posOfExpressionEnd

        return self.guessExpression(expression)

    def parseNonArrayPropertyValue(self):
        current = self.current()
        if current == CURLY_OPEN:
            return self.parseArray()
        elif current == QUOTE:
            return self.parseString()
        elif current == DOLLAR:
            return self.parseTranslationString()
        else:
            return self.parseUnknownExpression()

    def isValidVarnameChar(self, char):
        return char and char in VALID_NAME_CHAR

    def parsePropertyName(self):
        result = self.current()
        while(self.isValidVarnameChar(self.next())):
            result += self.current()

        return result

    def parseClassValue(self):
        result = self.dict()

        self.ensure(self.current() == CURLY_OPEN)
        self.next()
        self.parseWhitespace()

        while(self.current() != CURLY_CLOSE):
            self.parseProperty(result)
            self.parseWhitespace()

        self.next()

        return result

    def parseArray(self):
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

    def parseWhitespace(self):
        try:
            while self.isWhitespace():
                self.next()
        except IndexError:
            pass

    def isWhitespace(self):
        return self.raw[self.currentPosition] in ' \t\r\n' or ord(self.raw[self.currentPosition]) < 32

    def parseProperty(self, context):
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
                    self.currentPosition = len(self.raw)

            else:
                raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        else:
            raise ParseError('Unexpected value at pos {}'.format(self.currentPosition))

        context[name] = value

        self.parseWhitespace()
        self.ensure(self.current() == SEMICOLON)
        self.next()

    def translateString(self, txt: str) -> str:
        try:
            return self.translations[txt]
        except KeyError:
            return txt

    def parseTranslationString(self):
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

    def parse(self, raw, keep_order, translations):
        self.currentPosition = 0
        self.raw = raw
        self.translations = translations or {}
        if keep_order:
            self.dict = OrderedDict
        else:
            self.dict = dict

        result = self.dict()

        self.detectComment()
        self.parseWhitespace()
        while self.current():
            self.parseProperty(result)
            self.parseWhitespace()

        return result


def parse(raw, *, keep_order=False, translations=None):
    p = Parser()
    return p.parse(raw, keep_order, translations)
