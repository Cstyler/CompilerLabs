import re
import click


class LexException(Exception):
    pass


def find_max_prefix(text, start, main_pattern, add_pattern):
    def iter_regex_text(pattern):
        match_flag = False
        last_match = None
        for i in range(1, max_substring_len):
            prefix = text[start:start + i]
            match = pattern.fullmatch(prefix)
            if match is not None:
                last_match = match
                match_flag = True
            elif match is None and match_flag:
                return last_match, start + i - 2
        if match_flag:
            return last_match, start + (max_substring_len - 1) - 2

    max_substring_len = len(text) - start + 1
    if max_substring_len == 1:
        return None, None

    ret = iter_regex_text(main_pattern)
    if ret is None:
        ret = iter_regex_text(add_pattern)
        if ret is not None:
            return ret
    else:
        return ret
    raise LexException()


def parse(text):
    pattern = re.compile("(1+)|(0)|(\".*(?<!\\\)\")|([ \t\r\v\f]+)|(\n)|(@\"[^\"]*\"\"[^\"]*\")")
    add_pattern = re.compile("(@\"[\s\S]*\")")
    # '"([^"\\\\\n]|\\\\[n"t\\\\])*"'

    i = 0
    text_len = len(text)
    line_num = 1
    char_num = 1
    while i < text_len - 1:
        try:
            match, i = find_max_prefix(text, i, pattern, add_pattern)
            if match:
                token_ind, matched_string = next((i, group) for i, group
                                                 in enumerate(match.groups())
                                                 if group is not None)
                token_type = None
                if token_ind == 0 or token_ind == 1:
                    token_type = "NUMBER"
                elif token_ind == 2:
                    token_type = "REG_STRING"
                elif token_ind == 5:
                    token_type = "LET_STRING"
                elif token_ind == 4:
                    line_num += 1
                    char_num = 0
                if token_type:
                    print(f"{token_type} ({line_num}, {char_num}): {matched_string}")
                char_num += len(matched_string)
            if match is None:
                break
        except LexException as _:
            print(f"Syntax error {line_num}, {char_num}")
            i += 1
        i += 1


@click.command()
@click.option('--file', help='path to file')
def main(file: str):
    with open(file, 'r') as file_:
        text = file_.read()
    parse(text)


if __name__ == '__main__':
    main()
