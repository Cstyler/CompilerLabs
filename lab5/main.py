import click
from compiler import Compiler


@click.command()
@click.option('--file', help='path to file')
def main(file: str):
    with open(file, 'r') as file_:
        text = file_.read()
    compiler = Compiler()
    scanner = compiler.get_scanner(text)
    for token in scanner:
        print(token)
    compiler.output_messages()


if __name__ == '__main__':
    main()
