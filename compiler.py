class Scanner:
    def __init__(self):
        self.whitespaces = {'\n', '\r', '\t', '\v', '\f', ' '}
        self.symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '>', '/'}
        self.keywords = {'if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return'}
        self.symbol_table = ['break', 'else', 'if', 'int', 'repeat', 'return', 'until', 'void']
        self.tokens = {}
        self.errors = {}
        self.line_counter = 1

    def write_to_files(self):
        tokens_txt = open('tokens.txt', 'w+')
        tokens_txt.write('\n'.join([f"{line_no}.\t{' '.join(value)}" for line_no, value in self.tokens.items()]))
        tokens_txt.close()

        symbol_table_txt = open('symbol_table.txt', 'w+')
        symbol_table_txt.write('\n'.join([f'{i+1}.\t{s}' for i, s in enumerate(self.symbol_table)]))
        symbol_table_txt.close()

        lexical_errors_txt = open('lexical_errors.txt', 'w+')
        if len(self.errors) == 0:
            lexical_errors_txt.write('There is no lexical error.')
        else:
            lexical_errors_txt.write('\n'.join([f"{line_no}.\t{' '.join(value)}" for line_no, value in self.errors.items()]))
        lexical_errors_txt.close()

    def get_lookahead(self, i, chars):
        if i >= len(chars):
            return None
        return chars[i + 1]

    def get_next_token(self, chars, i):
        state = 1
        while True:
            if i >= len(chars):
                if state == 11:
                    self.add_error('Unclosed comment', comment)
                return 'FILE_ENDED', None, None
            char = chars[i]
            if char == '\n':
                self.line_counter += 1
            if state == 1:
                if char.isdigit():
                    state = 2
                    i += 1
                    num = char
                elif char.isalpha():
                    state = 4
                    i += 1
                    word = char
                elif char in self.symbols:
                    if char == '=' and self.get_lookahead(i, chars) == '=':
                        return 'SYMBOL', '==', i + 2
                    elif char == '/':
                        if self.get_lookahead(i, chars) == '*':
                            i += 2
                            comment = '/*'
                            state = 11
                        else:
                            self.add_error('Invalid input', char)
                            i += 1
                    elif char == '*' and self.get_lookahead(i, chars) == '/':
                        self.add_error('Unmatched comment', '*/')
                        i += 2
                    else:
                        return 'SYMBOL', char, i + 1
                elif char in self.whitespaces:
                    return 'WHITESPACE', char, i + 1
                else:
                    self.add_error('Invalid input', char)
                    i += 1
            elif state == 2:  # TODO need to check the correct error for sth like 23$$ i.e multiple invalid characters
                if char.isdigit():
                    num = num + char
                    i += 1
                elif char in self.symbols or char in self.whitespaces:
                    return 'NUM', num, i
                else:
                    self.add_error('Invalid number', num + char)
                    i += 1
                    state = 1
            elif state == 4:
                if char.isalpha() or char.isdigit():
                    word = word + char
                    i += 1
                elif char in self.symbols or char in self.whitespaces:
                    self.add_symbol(word)
                    return self.get_token(word), word, i
                else:
                    self.add_error('Invalid input', word + char)
                    i += 1
                    state = 1
            elif state == 11:
                if char == '*' and self.get_lookahead(i, chars) == '/':
                    i += 2
                    return 'COMMENT', comment, i
                else:
                    i += 1
                    comment += char

    def add_symbol(self, symbol):
        if symbol not in self.symbol_table:
            self.symbol_table.append(symbol)

    def add_error(self, message, error_chars):
        to_add = f"({error_chars if len(error_chars)<7 else (error_chars[:7] + f'...')}, {message})"
        if self.line_counter in self.errors.keys():
            self.errors[self.line_counter].append(to_add)
        else:
            self.errors[self.line_counter] = [to_add]

    def add_token(self, token, lexeme):
        to_add = f'({token}, {lexeme})'
        if self.line_counter in self.tokens.keys():
            self.tokens[self.line_counter].append(to_add)
        else:
            self.tokens[self.line_counter] = [to_add]

    def scanner_loop(self, lines):
        i = 0
        while i < len(lines):
            token, lexeme, new_i = self.get_next_token(lines, i)
            if token != 'WHITESPACE' and token != 'COMMENT' and token != 'FILE_ENDED':
                self.add_token(token, lexeme)
            if token == 'FILE_ENDED':
                break
            i = new_i
        self.write_to_files()

    def get_token(self, word):
        if word in self.keywords:
            return 'KEYWORD'
        else:
            return 'ID'


scanner = Scanner()
with open('input.txt') as f:
    lines = ''.join(f.readlines())
    scanner.scanner_loop(lines)
f.close()
