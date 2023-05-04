import json
from compiler import Scanner
import pandas as pd


class Table:
    def __init__(self, input_lines):
        self.scanner = Scanner()
        self.input_lines = input_lines
        with open('data.json') as f:
            data = json.loads(f.read())
            self.terminals = data["terminals"]
            self.non_terminals = data["non-terminals"]
            self.first = data["first"]
            self.follow = data["follow"]
            self.productions = data["productions"]
        f.close()

    def create_table(self):
        columns = self.terminals.copy()
        columns.append('$')
        columns.append('EPSILON')
        tbl = pd.DataFrame(columns=columns, index=self.non_terminals)
        for non_terminal in self.non_terminals:
            productions = self.productions[non_terminal]
            for prod in productions:
                to_first = prod[0]
                if to_first in self.non_terminals:
                    firsts = self.first[to_first]
                else:
                    firsts = [to_first]
                for first in firsts:
                    if first == 'EPSILON':
                        for terminal in self.follow[non_terminal]:
                            tbl[terminal][non_terminal] = prod
                            if terminal == '$':
                                tbl['$'][non_terminal] = prod
                    else:
                        tbl[first][non_terminal] = prod
        return tbl


with open('input.txt') as input_file:
    lines = ''.join(input_file.readlines())
    lines += ' '
    table = Table(lines)
input_file.close()

# print(table.terminals)
# print(table.non_terminals)
# print(table.first)
# print(table.follow)
# print(table.productions)
print(table.create_table())