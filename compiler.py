class Scanner:
    def __init__(self):
        self.tokens_txt = open('tokens.txt', 'w+')
        self.tokens_txt.close()
        self.symbol_table_txt = open('symbol_table.txt', 'w+')
        self.symbol_table_txt.close()
        self.lexical_errors_txt = open('lexical_errors.txt', 'w+')
        self.lexical_errors_txt.close()

    def get_next_token(self):
        pass

    def scanner_loop(self, line, line_counter):
        while True:
            self.get_next_token()
        pass


scanner = Scanner()
with open('input.txt') as f:
    line_counter = 0
    while True:
        line_counter += 1
        line = f.readline()
        if not line:
            break
        scanner.scanner_loop(line, line_counter)
        print(line_counter, ':  ', line)
f.close()
