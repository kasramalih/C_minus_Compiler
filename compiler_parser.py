from scanner import Scanner
from table_generator import Table
from anytree import Node, RenderTree


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
        found_errors = True
        errors =''
        i = 0
        token, lexeme, i = self.scanner.get_next_valid_token(self.chars, i)
        a = lexeme if token == 'KEYWORD' or token == 'SYMBOL' else token
        char = (token, lexeme)
        root = Node('Program')
        X = ('Program', None)
        self.stack.append(('$', Node('Program')))
        self.stack.append(X)
        while X[0] != '$':
            if X[0] == a:
                self.stack.pop()
                Node(pair(char[0], char[1]), parent=X[1])
                token, lexeme, i = self.scanner.get_next_valid_token(self.chars, i)
                char = (token, lexeme)
                a = lexeme if token == 'KEYWORD' or token == 'SYMBOL' else token
            elif X[0] in self.terminals:
                self.error()
            # elif not isinstance(self.table[a][X], list):
            #     self.error()
            else:
                # when production is EPSILON do not add it to stack!
                char = (token, lexeme)
                production = self.table[a][X[0]]
                self.stack.pop()
                if X[0] == 'Program':
                    next_par = root
                else:
                    next_par = Node(X[0], parent=X[1])
                if production == ['EPSILON']:
                    Node('epsilon', next_par)
                else:
                    for val in reversed(production):
                        self.stack.append((val, next_par))
            X = self.stack[-1]
        Node('$', root)

        #print(RenderTree(root).by_attr())
        self.write_to_files(RenderTree(root).by_attr(), False, errors)

    def error(self):
        print('error')

    def write_to_files(self, parse_tree, has_error, errors):
        parse_tree_txt = open('parse_tree.txt', 'w+', encoding="utf-8")
        parse_tree_txt.write(parse_tree)
        parse_tree_txt.close()

        syntax_errors_txt = open('syntax_errors.txt', 'w+')
        if not has_error:
            syntax_errors_txt.write('There is no syntax error.')
            syntax_errors_txt.close()

def pair(a, b):
    return '(' + a + ', ' + b + ')'
