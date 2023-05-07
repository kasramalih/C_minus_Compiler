from parser import Parser

with open('input.txt') as input_file:
    lines = ''.join(input_file.readlines())
    lines += ' '
input_file.close()
parser = Parser(lines)
parser.parse()
