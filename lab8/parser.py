import attr
from typing import List, Dict, Callable, Tuple, Any, Union, Optional

from compiler import Compiler
from exceptions import ParseException, GrammarException
from tokens import Token, T, NonTerminalToken, TerminalToken
from enum import Enum
from scanner import GrammarScanner

from tree import TerminalNode, NonTerminalNode
import pprint

EPSILON = None


@attr.s
class Alt:
    list_of_term = attr.ib()  # List[Term]

    def __iter__(self):
        return iter(self.list_of_term)


@attr.s
class Term:
    symbol: Union[Token, List[Alt]] = attr.ib()
    quantifier: Enum = attr.ib(default=None)


@attr.s
class Parser:
    text: str = attr.ib()
    T: Enum = attr.ib()
    sym: Token = None
    grammar_dict: Dict[Enum, List[Alt]] = dict()
    compiler: Compiler
    scanner: Callable
    first_set: Dict[Enum, set]

    def __post_init__(self, scanner_type: Callable, text: str):
        self.compiler = Compiler(scanner_type)
        self.scanner = self.compiler.get_scanner(text)

    def parse_terminal(self, terminal: T):
        sym = self.sym
        if sym.has_tag(terminal):
            self.next_token()
        else:
            raise ParseException(sym.coords, terminal)

    def next_token(self):
        self.sym = next(self.scanner)

    def first_set_for_chain(self, rhs: List[Alt]) -> set:
        if not rhs:
            return {EPSILON}
        res_set = set()
        for alt in rhs:
            # print(alt)
            res_set |= self.first_set_for_alt(alt)
        return res_set

    def first_set_for_alt(self, alt):
        print(alt, type(alt))
        if not alt.list_of_term:
            return {EPSILON}
        head_term, *tail_term = alt.list_of_term
        sym = head_term.symbol
        print(sym, type(sym))
        if isinstance(sym, TerminalToken):
            first_set_term = {self.get_token_name(sym)}
            if not (head_term.quantifier is None or head_term.quantifier == T.PLUS):
                first_set_term = first_set_term - {EPSILON}
                first_set_term |= self.first_set_for_alt(Alt(tail_term))
        elif not tail_term and isinstance(sym, NonTerminalToken):
            first_set_term = self.first_set[self.get_token_name(sym)].copy()
            if not (head_term.quantifier is None or head_term.quantifier == T.PLUS):
                first_set_term = first_set_term - {EPSILON}
                first_set_term |= self.first_set_for_alt(Alt(tail_term))
        elif isinstance(sym, NonTerminalToken):
            first_set_term = self.first_set[self.get_token_name(sym)].copy()
            if not (head_term.quantifier is None or head_term.quantifier == T.PLUS):
                first_set_term.add(EPSILON)
            if EPSILON in first_set_term:
                first_set_term = first_set_term - {EPSILON}
                first_set_term |= self.first_set_for_alt(Alt(tail_term))
        return first_set_term

    def build_first_set(self):
        self.first_set = {nt: set() for nt in iter(self.grammar_dict.keys())}
        while True:
            changed_flag = False
            for lhs, rhs in self.grammar_dict.items():
                first_rhs = self.first_set_for_chain(rhs)
                first_lhs = self.first_set[lhs]
                if not first_rhs == first_lhs:
                    changed_flag = True
                    first_lhs.update(first_rhs)
            if not changed_flag:
                break
        pprint.pprint(self.first_set)

    # (S) = [NT \= (rhs) \.]*.
    def parse(self):
        self.next_token()
        while self.sym.has_tag(T.NON_TERMINAL):
            sym = self.sym
            self.parse_terminal(T.NON_TERMINAL)
            self.parse_terminal(T.ASSIGN)
            rhs = self.parse_rhs()
            self.grammar_dict[self.get_token_name(sym)] = rhs
            self.parse_terminal(T.DOT)

    # (rhs) = (alt) [\| (alt)]*.
    def parse_rhs(self) -> List[Alt]:
        alt = self.parse_alt()
        rhs_list = [alt]
        while self.sym.has_tag(T.OR):
            self.parse_terminal(T.OR)
            alt = self.parse_alt()
            rhs_list.append(alt)
        return rhs_list

    # (alt) = [(term)(M)]*.
    def parse_alt(self) -> Alt:
        alt_list = []
        while self.sym.has_one_of_tags(T.NON_TERMINAL, T.TERMINAL, T.LPAREN):
            term = self.parse_term()
            quantifier = self.parse_m()
            if quantifier is not None:
                term.quantifier = quantifier
            alt_list.append(term)
        return Alt(alt_list)
    # (term) = NT|T|\[(rhs)\]
    def parse_term(self) -> Term:
        sym = self.sym
        if sym.has_tag(T.NON_TERMINAL):
            self.parse_terminal(T.NON_TERMINAL)
            return Term(sym, None)
        elif sym.has_tag(T.TERMINAL):
            self.parse_terminal(T.TERMINAL)
            return Term(sym, None)
        else:
            self.parse_terminal(T.LPAREN)
            rhs = self.parse_rhs()
            self.parse_terminal(T.RPAREN)
            return Term(rhs, None)

    # (M) = [\+|\*|\?]?
    def parse_m(self) -> Optional[Enum]:
        sym = self.sym
        if sym.has_one_of_tags(T.PLUS, T.QUEST_MARK, T.MUL):
            self.parse_terminal(sym.tag)
            return sym.tag

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


n = 100


# noinspection PyArgumentList
class GrammarParser(Parser):
    def __init__(self, text: str) -> None:
        super().__post_init__(GrammarScanner, text)
