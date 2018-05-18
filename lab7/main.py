import click
from parser import GrammarParser
from exceptions import ParseException
from pprint import pprint
import pickle, dill
from scanner import GrammarScanner


@click.command()
@click.option('--file', help='path to file')
def main(file: str):
    with open(file, 'r') as file_:
        text = file_.read()

    parser = GrammarParser(text)
    grammar_filename = 'grammar.pkl'
    try:
        parser.parse()
        grammar = parser.transform_tree_to_grammar()
        grammar.build_parse_table()
        ser_grammar = grammar.serialize()
        with open(grammar_filename, 'wb') as _file:
            pickle.dump(ser_grammar, _file)
        # new_parser = grammar.build_parser(GrammarScanner, text)
        # new_parser.parse()
        # pprint(new_parser.table)
        # new_parser.print_tree()
    except ParseException as e:
        print(e)


if __name__ == '__main__':
    main()
