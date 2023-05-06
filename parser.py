import pandas as pd

from compiler import Scanner
from table_generator import Table


class Parser:
    def __init__(self, input_chars):
        self.scanner = Scanner()
        self.stack = []
        self.chars = input_chars
        instance_of_table = Table()
        self.table = instance_of_table.create_table()
        self.terminals = instance_of_table.terminals
        self.non_terminals = instance_of_table.non_terminals
        self.first = instance_of_table.non_terminals
        self.follow = instance_of_table.follow
        self.productions = instance_of_table.productions

    def parse(self):
        i = 0
        token, lexeme, i = self.scanner.get_next_valid_token(self.chars, i)
        a = token
        X = 'Program'
        self.stack.append('$')
        self.stack.append('Program')
        while X != '$':
            if X == a:
                self.stack.pop()
                token, lexeme, i = self.scanner.get_next_valid_token(self.chars, i)
                a = token
            elif X in self.terminals:
                self.error()
            elif pd.isnull(self.table[a][X]):
                self.error()
            else:
                production = self.table[a][X]
                print(X, '->', production)
                self.stack.pop()
                for val in reversed(production):
                    self.stack.append(val)
            X = self.stack[-1]

    def error(self):
        pass


with open('input.txt') as input_file:
    lines = ''.join(input_file.readlines())
    lines += ' '
input_file.close()
parser = Parser(lines)
parser.parse()
