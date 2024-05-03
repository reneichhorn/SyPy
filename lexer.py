from time import time
LEXER_ERROR = 'ERROR'
LEXER_WARNING = 'WARNING'
LEXER_INFO = 'INFO'
DEBUG = False

STRINGENCAPSULE = "'"


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
    TOKENLITSTRING = 'string'
    TOKENAND = 'and'
    TOKENOR = 'or'
    TOKENEXCLAMATION = 'exclamation'
    TOKENNUMBER = 'number'
    TOKENPARENOPEN = 'parenopen'
    TOKENPARENCLOSE = 'parenclose'
    LITERALTOKENS = {
        ',': TOKENCOMMA,
        '*': TOKENSTAR,
        '=': TOKENEQUALS,
        '>': TOKENGREATER,
        '<': TOKENLESS,
        '.': TOKENDOT,
        ';': TOKENSEMICOLON,
        '!': TOKENEXCLAMATION,
        '(': TOKENPARENOPEN,
        ')': TOKENPARENCLOSE
        # "'": TOKENLITSTRING
    }
    KEYWORDTOKENS = [TOKENSELECT, TOKENFROM, TOKENWHERE, TOKENNULL, TOKENAND, TOKENOR, TOKENNUMBER]
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

    def __getLoc(self, tokenlen):
        return f'{self.linecount + 1}:{(self.cursor - self.bol - tokenlen) + 1}'

    def __isInBounds(self):
        if self.cursor >= len(self.content):
            return False
        return True

    def __chopChar(self):
        ch = self.content[self.cursor]
        self.cursor += 1
        return ch

    def __isLiterallyToken(self):
        return self.content[self.cursor] in TOKENS.LITERALTOKENS.keys()

    def __isString(self):
        return self.content[self.cursor] == STRINGENCAPSULE

    def __isNumber(self):
        return self.__isInBounds() and not self.content[self.cursor].isspace() and not self.__isLiterallyToken() and self.content[self.cursor].isnumeric()

    def __isAlnum(self):
        return self.__isInBounds() and not self.content[self.cursor].isspace() and not self.__isLiterallyToken() and self.content[self.cursor].isalnum()

    def nextToken(self):
        if not self.__isInBounds():
            log(LEXER_INFO, f'Reached EOF at {self.__getLoc(0)}')
            return None
        while self.__isInBounds() and self.content[self.cursor].isspace():
            if self.content[self.cursor] == '\n':
                self.linecount += 1
                _ = self.__chopChar()
                self.bol = self.cursor
            else:
                _ = self.__chopChar()
        tokenstring = []
        if self.__isInBounds() and self.content[self.cursor] in TOKENS.LITERALTOKENS.keys():
            token = self.content[self.cursor]
            tokenloc = self.__getLoc(len(token))
            self.cursor += 1
            return Token(token, TOKENS.LITERALTOKENS[token], tokenloc)
        if self.__isInBounds() and self.__isString():
            _ = self.__chopChar()
            stringtoken = []
            while self.__isInBounds() and not self.__isString():
                stringtoken.append(self.__chopChar())
            if not self.__isInBounds:
                log(LEXER_ERROR, 'Reached EOF but Stringliteral was not closed')
                quit(1)
            _ = self.__chopChar()
            token = ''.join(stringtoken)
            tokenloc = self.__getLoc(len(token))
            self.cursor += 1
            return Token(token, TOKENS.TOKENLITSTRING, tokenloc)
        if not self.__isNumber():
            while self.__isAlnum():
                # TODO:
                #   Tokenize Dates
                #   Tokenize more keywords like Group by, in, not
                #   Tokenize (, ), [, ], {, }
                tokenstring.append(self.__chopChar())
            ttype = TOKENS.TOKENSYMBOL
            token = ''.join(tokenstring).upper()
            tokenloc = self.__getLoc(len(tokenstring))
            if token in TOKENS.KEYWORDS.keys():
                ttype = TOKENS.KEYWORDS[token]
            return Token(token, ttype, tokenloc)
        if self.__isNumber():
            while self.__isNumber():
                tokenstring.append(self.__chopChar())

            ttype = TOKENS.TOKENNUMBER
            token = ''.join(tokenstring)
            tokenloc = self.__getLoc(len(tokenstring))
            return Token(token, ttype, tokenloc)
        if not self.__isInBounds():
            log(LEXER_ERROR, 'Reached EOF unexpected at {self.__getLoc(0)}')
            quit(1)


class Parser:
    def __init__(self, tokenlist):
        self.tokens = tokenlist
        self.current = 0
        self.state = 'n'

    def expectToken(self, expectedTokens, errors):
        if None in expectedTokens and self.current + 1 > len(self.tokens) - 1:
            msg = 'Expected no more tokens, but have more'
            log(LEXER_ERROR, msg)
            errors.append(msg)
        if None not in expectedTokens  and self.current + 1 > len(self.tokens) - 1:
            msg = f'Expected {" or ".join(expectedTokens)} but there are no more Tokens'
            log(LEXER_ERROR, msg)
            errors.append(msg)
        nextToken = self.tokens[self.current + 1]
        if None not in expectedTokens and nextToken.ttype not in expectedTokens:
            msg = f'Expected {" or ".join(expectedTokens)} but got "{nextToken.name}" of type "{nextToken.ttype}" at {nextToken.loc}'
            log(LEXER_ERROR, msg)
            errors.append(msg)
        return nextToken

    def parse(self):
        errors = []
        for token in self.tokens:
            log(LEXER_INFO, token)
            if self.current == 0:
                if token.ttype != TOKENS.TOKENSELECT:
                    msg = f'Query has to start with Select, but got {token.name}'
                    log(LEXER_ERROR, msg) 
                    errors.append(msg)
                self.current += 1
                continue
            match token.ttype:
                # TODO
                #   Handle Dates
                #   Handle Group by
                case TOKENS.TOKENSELECT:
                    _ = self.expectToken([TOKENS.TOKENSYMBOL, TOKENS.LITERALTOKENS['*'], TOKENS.TOKENLITSTRING, TOKENS.TOKENNUMBER], errors)
                    self.state = 's'
                case TOKENS.TOKENFROM:
                    self.state = 'f'
                    _ = self.expectToken([TOKENS.TOKENSYMBOL], errors)
                case TOKENS.TOKENWHERE:
                    _ = self.expectToken([TOKENS.TOKENSYMBOL, TOKENS.TOKENLITSTRING, TOKENS.TOKENNUMBER], errors)
                    self.state = 'w1'
                case TOKENS.TOKENSTAR:
                    _ = self.expectToken([TOKENS.TOKENCOMMA, TOKENS.TOKENFROM], errors)
                case TOKENS.TOKENSYMBOL | TOKENS.TOKENLITSTRING | TOKENS.TOKENNUMBER:
                    if self.state == 's':
                        _ = self.expectToken([TOKENS.TOKENCOMMA, TOKENS.TOKENFROM], errors)
                    if self.state == 'f':
                        _ = self.expectToken([TOKENS.TOKENSEMICOLON, TOKENS.TOKENWHERE], errors)
                    if self.state == 'w1':
                        _ = self.expectToken([TOKENS.TOKENEXCLAMATION, TOKENS.TOKENEQUALS, TOKENS.TOKENLESS, TOKENS.TOKENGREATER], errors)
                    if self.state == 'w2':
                        nextToken = self.expectToken([TOKENS.TOKENSEMICOLON, TOKENS.TOKENAND, TOKENS.TOKENOR], errors)
                        if nextToken in [TOKENS.TOKENAND, TOKENS.TOKENOR]:
                            self.state = 'w1'
                case TOKENS.TOKENEQUALS:
                    _ = self.expectToken([TOKENS.TOKENSYMBOL, TOKENS.TOKENNULL, TOKENS.TOKENLITSTRING, TOKENS.TOKENNUMBER], errors)
                    self.state = 'w2'
                case TOKENS.TOKENGREATER:
                    _ = self.expectToken([TOKENS.TOKENSYMBOL], errors)
                    self.state = 'w2'
                case TOKENS.TOKENLESS:
                    _ = self.expectToken([TOKENS.TOKENSYMBOL], errors)
                    self.state = 'w2'
                case TOKENS.TOKENCOMMA:
                    _ = self.expectToken([TOKENS.TOKENSYMBOL, TOKENS.TOKENLITSTRING, TOKENS.TOKENNUMBER], errors)
                case TOKENS.TOKENSEMICOLON:
                    _ = self.expectToken([TOKENS.TOKENSELECT, None], errors)
                case TOKENS.TOKENAND | TOKENS.TOKENOR:
                    _ = self.expectToken([TOKENS.TOKENSYMBOL, TOKENS.TOKENLITSTRING, TOKENS.TOKENNUMBER], errors)
                    self.state = 'w1'
                case TOKENS.TOKENEXCLAMATION:
                    _ = self.expectToken([TOKENS.TOKENEQUALS], errors)
                case TOKENS.TOKENNULL:
                    _ = self.expectToken([TOKENS.TOKENSEMICOLON, TOKENS.TOKENAND, TOKENS.TOKENOR], errors)
                case _:
                    msg = f'Unhandled token type {token.ttype}'
                    log(LEXER_ERROR, msg)
                    errors.append(msg)
            self.current += 1
            if self.current >= len(self.tokens) - 1:
                return errors


if __name__ == '__main__':
    teststring = """Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and (1 != Null);
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;
    Select\t\t *, Id, Name, 'case'            from       \n  Account Where '12' = '32' and 1 != Null;

    """
    start = time()
    lex = Lexer(teststring)
    tokens = []
    while token := lex.nextToken():
        tokens.append(token)
    par = Parser(tokens)
    errors = par.parse()

    end = time()
    if len(errors) > 0:
        for error in errors:
            print(error)
    print(f'Generating tokens and validating of {len(teststring.split("\n"))} lines and {len(teststring)} characters took {end - start} seconds')
