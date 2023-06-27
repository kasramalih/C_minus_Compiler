import json
import pandas as pd


class Table:
    def __init__(self):
        with open('dataj/data.json') as f:
            data = json.loads(f.read())
            self.terminals = data["terminals"]
            self.non_terminals = data["non-terminals"]
            self.first = data["first"]
            self.follow = data["follow"]
            self.productions = data["productions"]
            self.augmented_productions = data["augmented_productions"]
        f.close()

    def create_table(self):
        columns = self.terminals.copy()
        columns.append('$')
        columns.append('EPSILON')
        tbl = pd.DataFrame(columns=columns, index=self.non_terminals)
        for non_terminal in self.non_terminals:
            productions = self.productions[non_terminal]
            augmented_productions = self.augmented_productions[non_terminal]
            for prod, aug_prod in zip(productions, augmented_productions):
                check_firsts = True
                epsilon_check = False
                i = 0
                while check_firsts:
                    if i >= len(prod):
                        epsilon_check = True
                        break
                    val = prod[i]
                    if val in self.non_terminals:
                        firsts = self.first[val]
                    else:
                        firsts = [val]
                    check_firsts = False
                    for f in firsts:
                        if f == 'EPSILON':
                            i += 1
                            check_firsts = True
                        else:
                            tbl[f][non_terminal] = aug_prod
                if epsilon_check:
                    for terminal in self.follow[non_terminal]:
                        tbl[terminal][non_terminal] = aug_prod
                        if terminal == '$':
                            tbl['$'][non_terminal] = aug_prod
        return tbl
