import re

class ParserError(Exception):
    pass

class Lexer:
    def __init__(self, text):
        self.tokens = self.tokenize(text)
        self.current = 0

    def tokenize(self, text):
        token_specification = [
            ('LBRACE',    r'\{'),
            ('RBRACE',    r'\}'),
            ('SEMICOLON', r';'),
            ('EQUALS',    r'='),
            ('NUMBER',    r'\d+(\.\d+)?'),
            ('PIPE',      r'\|'),
            ('OP',        r'\+|\-|\*|\/'),
            ('NAME',      r'[A-Za-z_][A-Za-z0-9_]*'),
            ('STRING',    r'"[^"]*"'),
            ('SKIP',      r'[ \t\n]+'),
            ('MISMATCH',  r'.'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        get_token = re.compile(tok_regex).match
        line = text
        pos = 0
        tokens = []
        match = get_token(line)
        while match is not None:
            kind = match.lastgroup
            value = match.group(kind)
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
                tokens.append(('NUMBER', value))
            elif kind == 'STRING':
                tokens.append(('STRING', value.strip('"')))
            elif kind == 'NAME':
                # Проверяем на ключевые слова
                if value.lower() == 'let':
                    kind = 'LET'
                    value = value.lower()
                tokens.append((kind, value))
            elif kind == 'OP':
                tokens.append((kind, value))
            elif kind in ('EQUALS', 'SEMICOLON', 'PIPE', 'LBRACE', 'RBRACE'):
                tokens.append((kind, value))
            elif kind == 'SKIP':
                pass
            elif kind == 'MISMATCH':
                raise ParserError(f'Unexpected character {value}')
            pos = match.end()
            match = get_token(line, pos)
        tokens.append(('EOF', ''))
        return tokens

    def peek(self):
        return self.tokens[self.current]

    def next(self):
        self.current += 1

    def match(self, expected_type):
        if self.peek()[0] == expected_type:
            value = self.peek()[1]
            self.next()
            return value
        else:
            raise ParserError(f'Expected {expected_type}, got {self.peek()[0]}')

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.constants = {}

    def parse(self):
        result = {}
        while self.lexer.peek()[0] != 'EOF':
            if self.lexer.peek()[0] == 'LET':
                self.parse_constant()
            elif self.lexer.peek()[0] == 'LBRACE':
                result = self.parse_dict()
            else:
                raise ParserError(f'Unexpected token {self.lexer.peek()}')
        return result

    def parse_constant(self):
        self.lexer.match('LET')
        name = self.lexer.match('NAME')
        self.lexer.match('EQUALS')
        value = self.parse_value()
        self.lexer.match('SEMICOLON')
        self.constants[name] = value

    def parse_value(self):
        token_type, token_value = self.lexer.peek()
        if token_type == 'NUMBER':
            self.lexer.next()
            return token_value
        elif token_type == 'STRING':
            self.lexer.next()
            return token_value
        elif token_type == 'NAME':
            name = self.lexer.match('NAME')
            if name in self.constants:
                return self.constants[name]
            else:
                raise ParserError(f'Undefined constant {name}')
        elif token_type == 'LBRACE':
            return self.parse_dict()
        elif token_type == 'PIPE':
            return self.parse_expression()
        else:
            raise ParserError(f'Invalid value {self.lexer.peek()}')

    def parse_dict(self):
        self.lexer.match('LBRACE')
        result = {}
        while self.lexer.peek()[0] != 'RBRACE':
            key = self.lexer.match('NAME')
            self.lexer.match('EQUALS')
            value = self.parse_value()
            result[key] = value
        self.lexer.match('RBRACE')
        return result

    def parse_expression(self):
        self.lexer.match('PIPE')
        token_type, op = self.lexer.peek()
        if token_type == 'OP':
            op = self.lexer.match('OP')
        elif token_type == 'NAME':
            op = self.lexer.match('NAME')
            op = op.lower()
        else:
            raise ParserError(f'Expected operator, got {token_type}')
        args = []
        while self.lexer.peek()[0] != 'PIPE':
            arg = self.parse_value()
            args.append(arg)
        self.lexer.match('PIPE')
        return self.evaluate_expression(op, args)

    def evaluate_expression(self, op, args):
        if op == '+':
            return sum(args)
        elif op == '-':
            if len(args) != 2:
                raise ParserError('Subtraction requires exactly two operands')
            return args[0] - args[1]
        elif op == '*':
            result = 1
            for arg in args:
                result *= arg
            return result
        elif op == '/':
            if len(args) != 2:
                raise ParserError('Division requires exactly two operands')
            return args[0] / args[1]
        elif op == 'max':
            return max(args)
        elif op == 'pow':
            if len(args) != 2:
                raise ParserError('pow() requires exactly two operands')
            return args[0] ** args[1]
        else:
            raise ParserError(f'Unknown operator {op}')
