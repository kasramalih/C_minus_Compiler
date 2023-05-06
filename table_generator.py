import json
import pandas as pd


class Table:
    def __init__(self):
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
