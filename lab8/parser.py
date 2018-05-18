import attr
from typing import List, Dict, Callable, Tuple, Any

from compiler import Compiler
from exceptions import ParseException, GrammarException
from tokens import Token, T, NonTerminalToken, TerminalToken
from enum import Enum
from scanner import GrammarScanner

from tree import TerminalNode, NonTerminalNode

EPSILON = None


@attr.s
class Grammar:
    grammar_dict: Dict[Enum, Tuple[Tuple[Enum]]] = attr.ib()
    TermEnum: Enum = attr.ib()
    NonTermEnum: Enum = attr.ib()
    axiom: Enum = attr.ib()
    first_set_chain_dict: Dict = dict()

    def build_parse_table(self):
        self.build_first_set_non_term()
        self.build_follow_set()

        def check_ll1():
            if _tuple in self.parse_table:
                raise GrammarException(f"Not LL(1) Grammar. "
                                       f"On pair: {_tuple} there is two rules:"
                                       f" {rhs} and {self.parse_table[_tuple]}")

        self.parse_table = dict()
        for lhs, rhs_list in self.grammar_dict.items():
            for rhs in rhs_list:
                first_rhs = self.first_set_chain(rhs)
                for symbol in first_rhs:
                    if symbol == EPSILON:
                        continue
                    _tuple = (symbol, lhs)
                    check_ll1()
                    self.parse_table[_tuple] = rhs
                if EPSILON in first_rhs:
                    follow_lhs = self.follow_set[lhs]
                    for symbol in follow_lhs:
                        _tuple = (symbol, lhs)
                        check_ll1()
                        self.parse_table[_tuple] = rhs

    def build_parser(self, scanner_type: Callable, text: str):
        return Parser(scanner_type, text, self.TermEnum, self.NonTermEnum, self.parse_table, self.axiom)

    def first_set_chain(self, symbols: Tuple[Enum], cache=True):
        if cache and symbols in self.first_set_chain_dict:
            return self.first_set_chain_dict[symbols]
        if symbols:
            head, *tail = symbols
            tail = tuple(tail)
            if head in self.TermEnum:
                return {head}
            else:
                first_x = self.first_set[head].copy()
                if EPSILON in first_x:
                    first_x.remove(EPSILON)
                    first_set = first_x | self.first_set_chain(tail, cache)
                    self.first_set_chain_dict[symbols] = first_set
                    return first_set
                else:
                    self.first_set_chain_dict[symbols] = first_x
                    return first_x
        else:
            return {EPSILON}

    def build_first_set_non_term(self):
        self.first_set = {nt: set() for nt in iter(self.NonTermEnum)}
        while True:
            new_first = False
            for lhs, rhs_list in self.grammar_dict.items():
                for rhs in rhs_list:
                    rhs_first = self.first_set_chain(rhs, cache=False)
                    lhs_first = self.first_set[lhs]
                    if not rhs_first.issubset(lhs_first):
                        new_first = True
                        self.first_set[lhs].update(rhs_first)
            if not new_first:
                break

    def build_follow_set(self):
        self.follow_set = {nt: set() for nt in iter(self.NonTermEnum)}
        self.follow_set[self.axiom].add(self.TermEnum.END_OF_PROGRAM)
        for lhs, rhs_list in self.grammar_dict.items():
            for rhs in rhs_list:
                for i, symbol in enumerate(rhs):
                    if symbol in self.NonTermEnum:
                        tail = rhs[i + 1:]
                        first_tail = self.first_set_chain(tail) - {EPSILON}
                        self.follow_set[symbol].update(first_tail)
        while True:
            new_follow = False
            for lhs, rhs_list in self.grammar_dict.items():
                for rhs in rhs_list:
                    for i, symbol in enumerate(rhs):
                        if symbol in self.NonTermEnum:
                            tail = rhs[i + 1:]
                            if EPSILON in self.first_set_chain(tail):
                                lhs_follow = self.follow_set[lhs]
                                rhs_follow = self.follow_set[symbol]
                                if not lhs_follow.issubset(rhs_follow):
                                    new_follow = True
                                    rhs_follow.update(lhs_follow)
            if not new_follow:
                break


class Parser:
    def __init__(self, scanner_type: Callable, text: str, T: Enum):
        self.compiler = Compiler(scanner_type)
        self.scanner = self.compiler.get_scanner(text)
        self.text = text
        self.T = T

    def get_token_name(self, token: Token) -> str:
        if isinstance(token, NonTerminalToken):
            return self.compiler.get_name(token.code)
        elif isinstance(token, TerminalToken):
            return token.terminal_str
        else:
            return ""

    def token_repr(self, tok: Token):
        return f"{tok} {self.get_token_name(tok)}"

    def print_scanner(self):
        for token in self.compiler.get_scanner(self.text):
            print(self.token_repr(token))


# noinspection PyArgumentList
class GrammarParser(Parser):
    def __init__(self, text: str) -> None:
        super().__init__(GrammarScanner, text, T)
