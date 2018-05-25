from turtledemo import penrose

import click
from parser import GrammarParser, calc_expr_tree
from exceptions import ParseException
from pprint import pprint
import pickle


@click.command()
@click.option('--file', help='path to file')
def main(file: str):
    with open(file, 'r') as _file:
        text = _file.read()
    with open('grammar.pkl', 'rb') as _file:
        ser_grammar = pickle.load(_file)
    try:

        from scanner import ProgramScanner
        parser = ser_grammar.build_parser(ProgramScanner, text)
        parser.parse()
        # parser.print_scanner()
        # parser.compiler.output_messages()
        val = calc_expr_tree(parser.root)
        print(val)
    except ParseException as e:
        print(e)


if __name__ == '__main__':
    main()
