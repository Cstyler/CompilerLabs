from position import Position
from tokens import T, NonTerminalToken, TerminalToken, AxiomToken, SpecToken, CalcSpecToken, NumToken, CalcTag
import operator
from typing import Callable


def skip_by_pred(cur: Position, predicate: Callable):
    while predicate(cur):
        cur = next(cur)
    return cur


def transform_terminal(cur: Position):
    mirrored_symbols = {"(", ")", "=", ".", "|"}
    result_str_list = []

    while cur.is_terminal_symbol:
        if cur.cp == '\\':
            next_pos = next(cur)
            if next_pos.cp in mirrored_symbols:
                result_str_list.append(next_pos.cp)
                cur = next(next_pos)
                continue
        result_str_list.append(cur.cp)
        cur = next(cur)
    result_str = "".join(result_str_list)
    return cur, result_str


def GrammarScanner(text: str, compiler):
    cur = Position.default_position(text)
    whitespace_attrgetter = operator.attrgetter('is_white_space')
    is_letter_or_digit_attrgetter = operator.attrgetter('is_letter_or_digit')
    while cur.cp != -1:
        cur = skip_by_pred(cur, whitespace_attrgetter)
        if cur.cp == -1:
            break
        start = cur
        if cur.cp == '(':
            cur = next(cur)
            cur = skip_by_pred(cur, whitespace_attrgetter)
            ident_start = cur
            if cur.is_letter:
                cur = skip_by_pred(cur, is_letter_or_digit_attrgetter)
            else:
                compiler.add_message(True, "not ident inside of brackets", cur)
                cur = next(cur)
                continue

            ident_name = get_text_from_coords(cur, ident_start, text)
            axiom_flag = ident_name == 'axiom'
            if axiom_flag:
                cur = skip_by_pred(cur, whitespace_attrgetter)
                ident_start2 = cur
                if cur.is_letter:
                    cur = skip_by_pred(cur, is_letter_or_digit_attrgetter)
                else:
                    compiler.add_message(True, "not ident inside of brackets", cur)
                    cur = next(cur)
                    continue
                ident_name = get_text_from_coords(cur, ident_start2, text)
            cur = skip_by_pred(cur, whitespace_attrgetter)
            if cur.cp != ')':
                compiler.add_message(True, "bracket is not closed", cur)
                cur = next(cur)
                continue
            cur = next(cur)
            token_class = AxiomToken if axiom_flag else NonTerminalToken
            yield token_class(compiler.add_name(ident_name), start, cur)
        elif cur.cp == '=':
            cur = next(cur)
            yield SpecToken(T.ASSIGN, start, cur)
        elif cur.cp == '|':
            cur = next(cur)
            yield SpecToken(T.OR, start, cur)
        elif cur.cp == '.':
            cur = next(cur)
            yield SpecToken(T.DOT, start, cur)
        elif cur.is_terminal_symbol:
            cur, ident_name = transform_terminal(cur)
            yield TerminalToken(ident_name, start, cur)
        else:
            compiler.add_message(True, "lex error", cur)
            cur = next(cur)
    yield SpecToken(T.END_OF_PROGRAM, cur, cur)


def ProgramScanner(text: str, compiler):
    cur = Position.default_position(text)
    whitespace_attrgetter = operator.attrgetter('is_white_space')
    digit_attrgetter = operator.attrgetter('is_digit')
    while cur.cp != -1:
        cur = skip_by_pred(cur, whitespace_attrgetter)
        if cur.cp == -1:
            break
        start = cur
        if cur.cp == '(':
            cur = next(cur)
            yield CalcSpecToken(CalcTag.LPAREN, start, cur)
        elif cur.cp == ')':
            cur = next(cur)
            yield CalcSpecToken(CalcTag.RPAREN, start, cur)
        elif cur.cp == '+':
            cur = next(cur)
            yield CalcSpecToken(CalcTag.PLUS, start, cur)
        elif cur.cp == '*':
            cur = next(cur)
            yield CalcSpecToken(CalcTag.MUL, start, cur)
        elif cur.is_digit:
            cur = skip_by_pred(cur, digit_attrgetter)
            num = int(get_text_from_coords(cur, start, text))
            yield NumToken(num, start, cur)
        else:
            compiler.add_message(True, "lex error", cur)
            cur = next(cur)
    yield CalcSpecToken(CalcTag.END_OF_PROGRAM, cur, cur)


def get_text_from_coords(cur, start, text):
    return text[start.index: cur.index]
