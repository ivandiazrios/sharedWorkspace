from collections import OrderedDict

TOKEN_BEGIN_DICTIONARY = "TOKEN_BEGIN_DICTIONARY"
TOKEN_END_DICTIONARY = "TOKEN_END_DICTIONARY"
TOKEN_BEGIN_LIST = "TOKEN_BEGIN_LIST"
TOKEN_END_LIST = "TOKEN_END_LIST"
TOKEN_SEMICOLON = "TOKEN_SEMICOLON"
TOKEN_STRING = "TOKEN_STRING"
TOKEN_DATA = "TOKEN_DATA"
TOKEN_COMMA = "TOKEN_COMMA"
TOKEN_EQUALS = "TOKEN_EQUALS"
TOKEN_COMMENT = "TOKEN_COMMENT"
TOKEN_END = "TOKEN_END"
TOKEN_IDENTIFIER = "TOKEN_IDENTIFIER"
TOKEN_BEGIN_SECTION = "TOKEN_BEGIN_SECTION"
TOKEN_END_SECTION = "TOKEN_END_SECTION"

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in xrange(ord(c1), ord(c2) + 1):
        yield chr(c)

def isHex(x):
    return x.isdigit() or x in char_range('a', 'f') or x == ' '

def isIdentifierChar(x):
    return x.isalnum() or x in "/._-"

def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text) - len(suffix)]

class Token(object):
    def __init__(self, token_type, associatedValue):
        self.token_type = token_type
        self.associatedValue = associatedValue

    def __repr__(self):
        return "(%s, %s)" % (self.token_type, self.associatedValue)

    def __eq__(self, other):
        return type(other) == type(self) and self.token_type == other.token_type and self.associatedValue == other.associatedValue

    def __hash__(self):
        return (self.token_type, self.associatedValue).__hash__()

class Parser:
    def __init__(self, string_or_stream):
        self.input = string_or_stream
        if type(self.input) in (str, unicode):
            self.input = open(self.input, 'r')

        self.tokenizer = Tokenizer(self.input).tokenize()
        self.look_ahead = None

    def next_token(self):
        if self.look_ahead:
            out = self.look_ahead
            self.look_ahead = None
        else:
            out = self.tokenizer.next()

        return out

    def peek_token(self):
        self.look_ahead = self.tokenizer.next()
        return self.look_ahead

    def parse(self):
        plist = self.parse_tokens()
        self.parse_assert(self.next_token(), [TOKEN_END])
        return plist

    def parse_tokens(self):
        next_token = self.next_token()

        if next_token.token_type == TOKEN_BEGIN_DICTIONARY:
            return self.parse_dictionary()
        elif next_token.token_type == TOKEN_BEGIN_LIST:
            return self.parse_list()
        elif next_token.token_type == TOKEN_IDENTIFIER:
            return self.parse_identifier(next_token)
        elif next_token.token_type == TOKEN_STRING:
            return self.parse_string(next_token)
        elif next_token.token_type == TOKEN_DATA:
            return self.parse_data(next_token)
        elif next_token.token_type == TOKEN_COMMENT:
            return self.parse_tokens()
        else:
            self.parse_assert(next_token,
                              [TOKEN_BEGIN_DICTIONARY, TOKEN_BEGIN_LIST, TOKEN_IDENTIFIER, TOKEN_STRING, TOKEN_DATA])

    def parse_identifier(self, token):
        val = token.associatedValue
        if val.isdigit():
            val = int(val)
        return val

    def parse_string(self, token):
        return "%s" % token.associatedValue

    def parse_data(self, token):
        return "<%s>" % token.associatedValue

    def parse_dictionary(self):
        dictionary = OrderedDict()

        while True:
            if self.peek_token().token_type == TOKEN_END_DICTIONARY:
                _ = self.next_token()
                return dictionary

            k, v = self.parse_key_value()
            dictionary[k] = v

    def parse_key_value(self):
        key = self.next_token()
        self.parse_assert(key, [TOKEN_IDENTIFIER, TOKEN_STRING])
        self.parse_assert(self.tokenizer.next(), [TOKEN_EQUALS])
        value = self.parse_tokens()

        self.parse_assert(self.next_token(), [TOKEN_SEMICOLON])

        return self.parse_identifier(key), value

    def parse_list(self):
        array = []

        while True:
            peek_token = self.peek_token()
            if peek_token.token_type == TOKEN_COMMA:
                _ = self.next_token()
                peek_token = self.peek_token()

            if peek_token.token_type == TOKEN_END_LIST:
                _ = self.next_token()
                return array

            array.append(self.parse_tokens())

    def parse_assert(self, token, token_types):
        if token.token_type not in token_types:
            raise ValueError("Expected %s, got %s" % (','.join(token_types), token.token_type))

class Tokenizer:
    def __init__(self, string_or_stream):
        self.input = string_or_stream
        if self.input in (str, unicode):
            self.input = open(self.input, 'r')

    def tokenize(self, **kwargs):
        self.ignoring_comments = kwargs.get("ignoring_comments", True)
        self.look_ahead = None
        self.lastToken = None

        next_token = self.next_token()
        while next_token.token_type != TOKEN_END:
            self.lastToken = next_token
            yield next_token
            next_token = self.next_token()

        yield next_token

    def next_token(self):
        next_char = self.next_char()
        while next_char.isspace():
            next_char = self.next_char()

        if next_char == '':
            return Token(TOKEN_END, None)
        elif next_char == "/" and self.peek_is_comment():
            return self.process_comment()
        elif next_char == "\"":
            return Token(TOKEN_STRING, self.value_until_str('\"', initial_char=next_char, inclusive=True, ignore_if_escaped=True))
        elif next_char == "<":
            return Token(TOKEN_DATA, self.value_until_str(">", character_validation_func=isHex, initial_char=next_char))
        elif next_char == '{':
            return Token(TOKEN_BEGIN_DICTIONARY, None)
        elif next_char == '}':
            return Token(TOKEN_END_DICTIONARY, None)
        elif next_char == '(':
            return Token(TOKEN_BEGIN_LIST, None)
        elif next_char == ')':
            return Token(TOKEN_END_LIST, None)
        elif next_char == ';':
            return Token(TOKEN_SEMICOLON, None)
        elif next_char == ',':
            return Token(TOKEN_COMMA, None)
        elif next_char == "=":
            return Token(TOKEN_EQUALS, None)
        elif isIdentifierChar(next_char):
            return Token(TOKEN_IDENTIFIER, self.value_while(isIdentifierChar, initial_char=next_char))
        else:
            raise ValueError("Unknown char %s" % next_char)

    def peek_is_comment(self):
        peek_char = self.peek_char()
        return peek_char == "/" or peek_char == "*"

    def process_comment(self):
        peek_char = self.peek_char()
        if peek_char == "/":
            _ = self.next_char()
            token = Token(TOKEN_COMMENT, self.value_until_str("\n"))
        elif peek_char == "*":
            _ = self.next_char()
            token = Token(TOKEN_COMMENT, self.value_until_str("*/"))
        else:
            raise ValueError("Extraneous /")

        if self.ignoring_comments:
            return self.next_token()
        else:
            return token

    def value_while(self, character_validation_func, **kwargs):
        value = kwargs.get('initial_char', '')

        while True:
            peek_char = self.peek_char()

            if not peek_char:
                raise ValueError("Waiting for %s but file ended" % peek_char)

            if not character_validation_func(peek_char):
                return value

            value += self.next_char()


    def value_until_str(self, str, **kwargs):
        value = kwargs.get('initial_char', '')
        character_validation_func = kwargs.get('character_validation_func', (lambda _: True))
        inclusive = kwargs.get("inclusive", False)
        ignore_if_escaped = kwargs.get('ignore_if_escaped', False)

        while True:
            next_char = self.next_char()
            if not character_validation_func(next_char):
                raise ValueError("INVALID CHARACTER")

            value += next_char
            if value.endswith(str) and not (ignore_if_escaped and value.endswith('\\' + str)):
                if inclusive:
                    return value
                else:
                    return strip_end(value, str)

    def next_char(self):
        return self.input.read(1)

    def peek_char(self):
        pos = self.input.tell()
        char = self.input.read(1)
        self.input.seek(pos)
        return char