from anytree import Node, RenderTree

from codegen import Codegen
from scanner import Scanner
from table_generator import Table


class Parser:
    def __init__(self, input_chars):
        self.scanner = Scanner()
        self.stack = []
        self.chars = input_chars
        instance_of_table = Table()
        self.table, self.nt_to_id, self.t_to_id = instance_of_table.create_table()
        self.terminals = instance_of_table.terminals
        self.non_terminals = instance_of_table.non_terminals
        self.first = instance_of_table.non_terminals
        self.follow = instance_of_table.follow
        self.productions = instance_of_table.productions
        self.parser_error = {}
        self.codegen = Codegen()

    def parse(self):
        found_errors = False
        unexpected_EOF = False
        errors = []
        i = 0
        token, lexeme, i = self.scanner.get_next_valid_token(self.chars, i)
        a = lexeme if token == 'KEYWORD' or token == 'SYMBOL' else token
        char = (token, lexeme)
        root = Node('Program')
        X = ('Program', None)
        self.stack.append(('$', Node('Program')))
        self.stack.append(X)
        while X[0] != '$':
            if X[0].startswith("#"):
                self.codegen.code_gen(X[0], lexeme, self.scanner.line_counter)
                Node(X[0], parent=X[1])
                self.stack.pop()
            elif X[0] == a:
                self.stack.pop()
                Node(pair(char[0], char[1]), parent=X[1])
                token, lexeme, i = self.scanner.get_next_valid_token(self.chars, i)
                char = (token, lexeme)
                a = lexeme if token == 'KEYWORD' or token == 'SYMBOL' else token
            elif X[0] in self.terminals:  # not a terminal
                found_errors = True
                self.error('missing ' + X[0], errors)
                self.stack.pop()
            elif not isinstance(self.table[self.t_to_id[a]][self.nt_to_id[X[0]]], list):  # empty table cell
                found_errors = True
                if a in self.follow[X[0]]:
                    self.error('missing ' + X[0], errors)
                    self.stack.pop()
                else:
                    if a == "$":
                        unexpected_EOF = True
                        self.error('Unexpected EOF', errors)
                        break
                    else:
                        self.error('illegal ' + a, errors)
                        token, lexeme, i = self.scanner.get_next_valid_token(self.chars, i)
                        char = (token, lexeme)
                        a = lexeme if token == 'KEYWORD' or token == 'SYMBOL' else token
            else:
                # when production is EPSILON do not add it to stack!
                char = (token, lexeme)
                production = self.table[self.t_to_id[a]][self.nt_to_id[X[0]]]
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
        if not unexpected_EOF:
            Node('$', root)
        # print(self.codegen.ss)

        write_program_block(self.codegen.pb, self.codegen.semantic_errors)
        write_semantic_errors(self.codegen.semantic_errors)
        # print(RenderTree(root).by_attr())
        # UniqueDotExporter(root).to_picture("output.png")
        write_to_files(RenderTree(root).by_attr(), found_errors, errors)

    def error(self, message, errors):
        errors.append('#' + str(self.scanner.line_counter) + ' : syntax error, ' + str(message))


def write_semantic_errors(errors):
    error_text = open('semantic_errors.txt', 'w+', encoding='utf-8')
    if errors:
        error_text.write('\n'.join(errors))
    else:
        error_text.write('The input program is semantically correct.')


def write_program_block(pb, semantic_error_found):
    pb_txt = open('output.txt', 'w+', encoding="utf-8")
    if semantic_error_found:
        pb_txt.write("The output code has not been generated.")
        pb_txt.close()
    else:
        pb_str = ""
        for i in range(len(pb)):
            pb_str += str(i) + '\t' + pb[i] + '\n'
        pb_txt.write(pb_str)
    pb_txt.close()


def write_to_files(parse_tree, has_error, errors):
    parse_tree_txt = open('parse_tree.txt', 'w+', encoding="utf-8")
    parse_tree_txt.write(parse_tree)
    parse_tree_txt.close()

    syntax_errors_txt = open('syntax_errors.txt', 'w+')
    if not has_error:
        syntax_errors_txt.write('There is no syntax error.')
    else:
        syntax_errors_txt.write('\n'.join(errors) + '\n')
    syntax_errors_txt.close()


def pair(a, b):
    return '(' + a + ', ' + b + ')'
