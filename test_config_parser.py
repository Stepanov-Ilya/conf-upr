import unittest

from config_parser import Lexer, Parser, ParserError


class TestLexer(unittest.TestCase):
    def test_tokenize_numbers(self):
        lexer = Lexer('123 45.67')
        tokens = lexer.tokens[:-1]  # Исключаем EOF
        expected = [('NUMBER', 123), ('NUMBER', 45.67)]
        self.assertEqual(tokens, expected)

    def test_tokenize_names(self):
        lexer = Lexer('LET MAX_CONNECTIONS = 100;')
        tokens = lexer.tokens[:-1]
        expected = [
            ('LET', 'let'),
            ('NAME', 'MAX_CONNECTIONS'),
            ('EQUALS', '='),
            ('NUMBER', 100),
            ('SEMICOLON', ';')
        ]
        self.assertEqual(tokens, expected)

    def test_tokenize_operations(self):
        lexer = Lexer('|+ 1 2|')
        tokens = lexer.tokens[:-1]
        expected = [
            ('PIPE', '|'),
            ('OP', '+'),
            ('NUMBER', 1),
            ('NUMBER', 2),
            ('PIPE', '|')
        ]
        self.assertEqual(tokens, expected)

    def test_tokenize_invalid_character(self):
        with self.assertRaises(ParserError):
            Lexer('@')


class TestParser(unittest.TestCase):
    def test_parse_constant(self):
        lexer = Lexer('let A = 10;')
        parser = Parser(lexer)
        parser.parse_constant()
        self.assertEqual(parser.constants['A'], 10)

    def test_parse_value_number(self):
        lexer = Lexer('42')
        parser = Parser(lexer)
        value = parser.parse_value()
        self.assertEqual(value, 42)

    def test_parse_value_constant(self):
        lexer = Lexer('A')
        parser = Parser(lexer)
        parser.constants['A'] = 5
        value = parser.parse_value()
        self.assertEqual(value, 5)

    def test_parse_value_undefined_constant(self):
        lexer = Lexer('B')
        parser = Parser(lexer)
        with self.assertRaises(ParserError):
            parser.parse_value()

    def test_parse_expression_addition(self):
        lexer = Lexer('|+ 1 2 3|')
        parser = Parser(lexer)
        value = parser.parse_expression()
        self.assertEqual(value, 6)

    def test_parse_expression_subtraction(self):
        lexer = Lexer('|- 10 4|')
        parser = Parser(lexer)
        value = parser.parse_expression()
        self.assertEqual(value, 6)

    def test_parse_expression_multiplication(self):
        lexer = Lexer('|* 2 3 4|')
        parser = Parser(lexer)
        value = parser.parse_expression()
        self.assertEqual(value, 24)

    def test_parse_expression_division(self):
        lexer = Lexer('|/ 20 5|')
        parser = Parser(lexer)
        value = parser.parse_expression()
        self.assertEqual(value, 4)

    def test_parse_expression_max(self):
        lexer = Lexer('|max 1 5 3|')
        parser = Parser(lexer)
        value = parser.parse_expression()
        self.assertEqual(value, 5)

    def test_parse_expression_pow(self):
        lexer = Lexer('|pow 2 3|')
        parser = Parser(lexer)
        value = parser.parse_expression()
        self.assertEqual(value, 8)

    def test_parse_expression_invalid_operator(self):
        lexer = Lexer('|unknown 1 2|')
        parser = Parser(lexer)
        with self.assertRaises(ParserError):
            parser.parse_expression()

    def test_parse_dictionary(self):
        lexer = Lexer('{ A = 1 B = 2 }')
        parser = Parser(lexer)
        result = parser.parse_dict()
        expected = {'A': 1, 'B': 2}
        self.assertEqual(result, expected)

    def test_parse_nested_dictionary(self):
        lexer = Lexer('{ OUTER = { INNER = 5 } }')
        parser = Parser(lexer)
        result = parser.parse_dict()
        expected = {'OUTER': {'INNER': 5}}
        self.assertEqual(result, expected)

    def test_parse_full_configuration(self):
        text = '''
        let A = 5;
        let B = 10;
        {
            SUM = |+ A B|
            PRODUCT = |* A B|
            MAX = |max A B|
        }
        '''
        lexer = Lexer(text)
        parser = Parser(lexer)
        result = parser.parse()
        expected = {
            'SUM': 15,
            'PRODUCT': 50,
            'MAX': 10
        }
        self.assertEqual(result, expected)

    def test_syntax_error_missing_semicolon(self):
        lexer = Lexer('let A = 5')
        parser = Parser(lexer)
        with self.assertRaises(ParserError):
            parser.parse_constant()

    def test_syntax_error_unexpected_token(self):
        lexer = Lexer('unexpected')
        parser = Parser(lexer)
        with self.assertRaises(ParserError):
            parser.parse()


if __name__ == '__main__':
    unittest.main()
