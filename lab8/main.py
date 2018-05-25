import click
from parser import GrammarParser
from exceptions import ParseException
from pprint import pprint


@click.command()
@click.option('--file', help='path to file')
def main(file: str):
    with open(file, 'r') as file_:
        text = file_.read()
    parser = GrammarParser(text)
    try:
        parser.parse()
        # pprint(parser.grammar_dict)
        parser.build_first_set()
        # parser.print_scanner()
    except ParseException as e:
        print(e)


if __name__ == '__main__':
    main()
