import click
from parser import GrammarParser, calc_expr_tree
from exceptions import ParseException
from pprint import pprint
import pickle

import tokens
from enum import Enum, auto

class Tag(Enum):
    LP = auto()
    RP = auto()
    atom = auto()
    END_OF_PROGRAM = auto()



def LispLexer(text, compiler):
    pos = tokens.Position("", 1, 1, 1)
    yield tokens.Token(Tag.LP, pos, pos)
    yield tokens.Token(Tag.atom, pos, pos)
    yield tokens.Token(Tag.atom, pos, pos)
    yield tokens.Token(Tag.RP, pos, pos)
    yield tokens.Token(Tag.END_OF_PROGRAM, pos, pos)



@click.command()
@click.option('--file', help='path to file')
def main(file: str):
    # with open(file, 'r') as _file:
    #     text = _file.read()
    with open('grammar.pkl', 'rb') as _file:
        ser_grammar = pickle.load(_file)
    try:
        pprint(ser_grammar.parse_table)
        parser = ser_grammar.build_parser(LispLexer, "")
        parser.parse()
        parser.print_scanner()
        parser.compiler.output_messages()
        # val = calc_expr_tree(parser.root)
        # print(val)
    except ParseException as e:
        print(e)


if __name__ == '__main__':
    main()
