LEXER_ERROR = 'ERROR'
LEXER_WARNING = 'WARNING'
LEXER_INFO = 'INFO'
DEBUG = True


class TOKENS:
    TOKENEQUALS = 'equals'
    TOKENGREATER = 'greater'
    TOKENLESS = 'less'
    TOKENSEMICOLON = 'semicolon'
    TOKENCOMMA = 'comma'
    TOKENSTAR = 'star'
    TOKENDOT = 'dot'
    TOKENSELECT = 'select'
    TOKENFROM = 'from'
    TOKENWHERE = 'where'
    TOKENNULL = 'null'
    TOKENSYMBOL = 'symbol' 
    LITERALTOKENS = {
            ',': TOKENCOMMA,
            '*': TOKENSTAR,
            '=': TOKENEQUALS,
            '>': TOKENGREATER,
            '<': TOKENLESS,
            '.': TOKENDOT,
            ';': TOKENSEMICOLON
            }
    KEYWORDTOKENS = [TOKENSELECT, TOKENFROM, TOKENWHERE, TOKENNULL]
    KEYWORDS = {token.upper(): token for token in KEYWORDTOKENS}


class Token:
    def __init__(self, tokenstring, ttype, loc):
        self.name = tokenstring
        self.ttype = ttype
        self.loc = loc

    def __str__(self):
        return f'{self.loc} - "{self.name}" - {self.ttype}'


def log(type, msg):
    if DEBUG:
        print(f'{type}: {msg}')


class Lexer:
    def __init__(self, text):
        self.content = text
        self.cursor = 0
        self.bol = 0
        self.linecount = 0

    def __getLoc(self):
        return f'{self.linecount + 1}:{(self.cursor - self.bol) + 1}'

    def __isInBounds(self):
        if self.cursor >= len(self.content):
            return False
        return True

    def __chopChar(self):
        ch = self.content[self.cursor]
        self.cursor += 1
        return ch

    def __isComma(self):
        return self.content[self.cursor] == ','

    def __isSpecial(self):
        return self.content[self.cursor] in TOKENS.LITERALTOKENS.keys()

    def nextToken(self):
        if not self.__isInBounds():
            log(LEXER_INFO, f'Reached EOF at {self.__getLoc()}')
            return None
        while self.content[self.cursor].isspace():
            if self.content[self.cursor] == '\n':
                self.linecount += 1
                _ = self.__chopChar()
                self.bol = self.cursor
            else:
                _ = self.__chopChar()
        tokenstring = []
        if self.__isInBounds() and self.content[self.cursor] in TOKENS.LITERALTOKENS.keys():
            token = self.content[self.cursor]
            tokenloc = self.__getLoc()
            self.cursor += 1
            return Token(token, TOKENS.LITERALTOKENS[token], tokenloc)
        while self.__isInBounds() and not self.content[self.cursor].isspace() and not self.__isSpecial():
            # TODO: 
            #   Tokenize Strings
            #   Tokenize Numbers
            #   Tokenize Dates
            #   Tokenize And
            #   Tokenize Or
            tokenstring.append(self.__chopChar())
        if self.__isInBounds() and self.__isSpecial:
            self.cursor -= 1
        token = ''.join(tokenstring).upper()
        tokenloc = self.__getLoc()
        ttype = TOKENS.TOKENSYMBOL
        if token in TOKENS.KEYWORDS.keys():
            ttype = TOKENS.KEYWORDS[token]
        self.cursor += 1
        return Token(token, ttype, tokenloc)


class Parser:
    def __init__(self, tokenlist):
        self.tokens = tokenlist
        self.current = 0
        self.state = 'n'

    def expectToken(self, expectedTokens):
        if self.current + 1 > len(self.tokens) - 1:
            log(LEXER_ERROR, f'Expected {" or ".join(expectedTokens)} but there are no more Tokens')
            quit(1)
        nextToken = self.tokens[self.current + 1]
        if nextToken.ttype not in expectedTokens:
            log(LEXER_ERROR, f'Expected {" or ".join(expectedTokens)} but got "{nextToken.name}" of type "{nextToken.ttype}" at {nextToken.loc}')
            quit(1)
        return True

    def parse(self):
        for token in self.tokens:
            print(token)
            match token.ttype:
                case TOKENS.TOKENSELECT:
                    self.expectToken([TOKENS.TOKENSYMBOL, TOKENS.LITERALTOKENS['*']])
                    self.state = 's'
                case TOKENS.TOKENFROM:
                    self.state = 'f'
                    self.expectToken([TOKENS.TOKENSYMBOL])
                case TOKENS.TOKENWHERE:
                    self.expectToken([TOKENS.TOKENSYMBOL])
                    self.state = 'w1'
                case TOKENS.TOKENSTAR:
                    self.expectToken([TOKENS.TOKENCOMMA, TOKENS.TOKENFROM])
                case TOKENS.TOKENSYMBOL:
                    if self.state == 's':
                        self.expectToken([TOKENS.TOKENCOMMA, TOKENS.TOKENFROM])
                    if self.state == 'f':
                        self.expectToken([TOKENS.TOKENSEMICOLON, TOKENS.TOKENWHERE])
                    if self.state == 'w1':
                        self.expectToken([TOKENS.TOKENEQUALS, TOKENS.TOKENLESS, TOKENS.TOKENGREATER])
                    if self.state == 'w2':
                        self.expectToken([TOKENS.TOKENSEMICOLON])
                        # TODO
                        # Expect AND or OR Tokens
                case TOKENS.TOKENEQUALS:
                    self.expectToken([TOKENS.TOKENSYMBOL, TOKENS.TOKENNULL])
                    self.state = 'w2'
                case TOKENS.TOKENGREATER:
                    self.expectToken([TOKENS.TOKENSYMBOL])
                    self.state = 'w2'
                case TOKENS.TOKENLESS:
                    self.expectToken([TOKENS.TOKENSYMBOL])
                    self.state = 'w2'
                case TOKENS.TOKENCOMMA:
                    self.expectToken([TOKENS.TOKENSYMBOL])
                case TOKENS.TOKENSEMICOLON:
                    continue
                case _:
                    print(token.ttype)
                    log(LEXER_ERROR, 'UNREACHABLE')
                    quit(1)
            self.current += 1


teststring = 'Select\t\t *, Id, Name             from       \n  Account Where 1=1;'
lex = Lexer(teststring)
tokens = []
while token := lex.nextToken():
    tokens.append(token)

par = Parser(tokens)
par.parse()

