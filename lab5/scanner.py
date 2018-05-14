from position import Position
from tokens import Token, T
from typing import Union, Callable, Optional, Tuple


class Automata:
    def __init__(self, table: list, lexical_domains: list, symbols_map: Callable):
        self.table = table
        self.lexical_domains = lexical_domains
        self.symbols_map = symbols_map

    def get_token(self, pos: Position):
        state = 0
        start = pos
        while True:
            class_ = self.symbols_map(pos.cp)
            new_state = self.table[state][class_]
            lexical_domain = self.lexical_domains[state]
            if new_state == -1:
                if lexical_domain is None:
                    return
                else:
                    return lexical_domain, start, pos
            pos = next(pos)
            state = new_state

def Scanner(text: str, compiler):
    table = [
        # (, ), {, }, i, f, t, h, e, n, l, s, oth_let, \d, ws, other, eop
        [1, 2, 3, -1, 6, 5, 8, 5, 12, 5, 5, 5, 16, 17, 18, -1, 19],  # start
        [-1] * 17,  # ( 1
        [-1] * 17,  # ) 2
        [3] * 3 + [4] + [3] * 12 + [-1], # { 3
        [-1] * 16,  # } COMMENT 4
        [-1] * 4 + [5] * 10 + [-1] * 3,  # id 5
        [-1] * 4 + [5] * 1 + [7] + [5] * 8 + [-1] * 3,  # i 6
        [-1] * 4 + [5] * 10 + [-1] * 3,  # f 7
        [-1] * 4 + [5] * 3 + [9] + [5] * 6 + [-1] * 3,  # t 8
        [-1] * 4 + [5] * 4 + [10] + [5] * 5 + [-1] * 3,  # h 9
        [-1] * 4 + [5] * 5 + [11] + [5] * 4 + [-1] * 3,  # e 10
        [-1] * 4 + [5] * 10 + [-1] * 3,  # n 11
        [-1] * 4 + [5] * 6 + [13] + [5] * 3 + [-1] * 3,  # e 12
        [-1] * 4 + [5] * 7 + [14] + [5] * 2 + [-1] * 3,  # l 13
        [-1] * 4 + [5] * 4 + [15] + [5] * 5 + [-1] * 3,  # s 14
        [-1] * 4 + [5] * 10 + [-1] * 3,  # e 15
        [-1] * 4 + [5] * 9 + [-1] * 4,  # oth_let 16
        [-1] * 13 + [17] + [-1] * 3,  # digit 17
        [-1] * 14 + [18] + [-1] * 2,  # ws 18
        [-1] * 17  # eop 19
    ]
    lexical_domains = [
        None,
        T.LPAREN,
        T.RPAREN,
        None,
        T.COMMENT,
        T.IDENT,
        None,
        T.IF_KEYWORD,
        None, None, None,
        T.THEN_KEYWORD,
        None, None, None,
        T.ELSE_KEYWORD,
        T.IDENT,
        T.NUMBER,
        T.SPACE,
        T.END_OF_PROGRAM
    ]

    def symbols_map(x: Union[str, int]):
        if x == -1:
            return 16
        one_length_symbols = {
            '(': 0,
            ')': 1,
            '{': 2,
            '}': 3,
            'i': 4,
            'f': 5,
            't': 6,
            'h': 7,
            'e': 8,
            'n': 9,
            'l': 10,
            's': 11
        }
        if x in one_length_symbols.keys():
            return one_length_symbols[x]
        if x.isalpha(): return 12
        if '0' < x < '9':
            return 13
        if x in ' \t\n\r\v\f':
            return 14
        return 15

    automata = Automata(table, lexical_domains, symbols_map)
    cur = Position.default_position(text)
    while cur.cp != -1:
        try:
            lex_domain, start, follow = automata.get_token(cur)
            yield Token(lex_domain, start, follow)
            cur = follow
        except TypeError:
            compiler.add_message(True, "lex error", cur)
            cur = next(cur)
