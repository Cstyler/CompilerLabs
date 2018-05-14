import click
from parser import GrammarParser, calc_expr_tree
from exceptions import ParseException
from pprint import pprint


@click.command()
@click.option('--file', help='path to file')
@click.option('--test_file', help='path to calc test file')
def main(file: str, test_file: str):
    with open(file, 'r') as file_:
        text = file_.read()

    with open(test_file, 'r') as _file:
        test_text = _file.read()
    parser = GrammarParser(text)
    try:
        parser.parse()
        grammar = parser.transform_tree_to_grammar()
        grammar.build_parse_table()

        # calculator
        # from scanner import ProgramScanner
        # new_parser = grammar.build_parser(ProgramScanner, test_text)
        # new_parser.parse()
        # new_parser.print_scanner()
        # new_parser.compiler.output_messages()
        # val = calc_expr_tree(new_parser.root)
        # print(val)

        from scanner import GrammarScanner
        new_parser = grammar.build_parser(GrammarScanner, text)
        new_parser.parse()
        # pprint(grammar.parse_table)
        new_parser.print_tree()
    except ParseException as e:
        print(e)


if __name__ == '__main__':
    main()
