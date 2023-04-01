class Scanner:
    def __init__(self):
        self.whitespaces = {'\n', '\r', '\t', '\v', '\f', ' '}
        self.symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '>', '==', '/'}
        self.keywords = {'if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return'}
        self.tokens_txt = open('tokens.txt', 'w+')
        self.tokens_txt.close()
        self.symbol_table_txt = open('symbol_table.txt', 'w+')
        self.symbol_table_txt.close()
        self.lexical_errors_txt = open('lexical_errors.txt', 'w+')
        self.lexical_errors_txt.close()

    def get_lookahead(self, i, chars):
        return chars[i + 1]

    def get_next_token(self, chars, i, line_counter):
        state = 1
        while True:
            char = chars[i]
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
                    elif char == '/' and self.get_lookahead(i, chars) == '*':
                        state = 11
                    else:
                        return 'SYMBOL', char, i + 1
                elif char in self.whitespaces:
                    return 'WHITESPACE', char, i + 1
                else:
                    state = -1
                    return 'ERROR', char, i + 1
            elif state == 2:
                if char.isdigit():
                    num = num + char
                    i += 1
                elif char.isalpha():
                    return 'ERROR', num + char, i + 1
                else:
                    return 'NUM', num, i
            elif state == 4:
                if char.isalpha() or char.isdigit():
                    word = word + char
                    i += 1
                else:
                    return self.get_token(word), word, i

        return token, lexeme, new_i

    def scanner_loop(self, line, line_counter):
        i = 0
        while i < len(line):
            token, new_i = self.get_next_token(line, i, line_counter)
            i = new_i
        pass

    def get_token(self, word):
        if word in self.keywords:
            return 'KEYWORD'
        else:
            return 'ID'


scanner = Scanner()
with open('input.txt') as f:
    line_counter = 0
    result = ''.join(f.readlines())
    for i in range(len(result)):
        print(result[i] == '\r\f\v')
    # while True:
    #     line_counter += 1
    #     line = f.readline()
    #     if not line:
    #         break
    #     # scanner.scanner_loop(line, line_counter)
    #     print(line_counter, ':  ', line)
f.close()
