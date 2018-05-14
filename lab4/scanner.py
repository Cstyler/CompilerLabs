from position import Position
from tokens import IdentToken, KeywordToken, FunctionNameToken, T, SpecToken


def Scanner(text: str, compiler):
    ident_start_letters = {'$', '@', '%'}
    keywords_strings = {'sub': T.SUB_KEYWORD,
                        'if': T.IF_KEYWORD,
                        'unless': T.UNLESS_KEYWORD}
    cur = Position.default_position(text)
    while cur.cp != -1:
        while cur.is_white_space:
            cur = next(cur)
        start = cur
        if cur.cp in ident_start_letters:
            cur = next(cur)
            while cur.is_letter_or_digit:
                cur = next(cur)
            ident_name = text[start.index: cur.index]
            yield IdentToken(compiler.add_name(ident_name), start, cur)
        elif cur.is_letter:
            cur = next(cur)
            while cur.is_letter_or_digit:
                cur = next(cur)
            ident_name = text[start.index: cur.index]
            if ident_name in keywords_strings:
                yield KeywordToken(keywords_strings[ident_name], start, cur)
            else:
                yield FunctionNameToken(compiler.add_name(ident_name), start, cur)
        else:
            compiler.add_message(True, "lex error", cur)
            cur = next(cur)
    yield SpecToken(T.END_OF_PROGRAM, cur, cur)
