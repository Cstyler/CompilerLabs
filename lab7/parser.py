import attr
from typing import List, Dict, Callable, Tuple, Any

from compiler import Compiler
from exceptions import ParseException, GrammarException
from tokens import Token, T, AxiomToken, NonTerminalToken, TerminalToken, NumToken
from enum import Enum
from scanner import GrammarScanner

from tree import TerminalNode, NonTerminalNode

EPSILON = None


# noinspection PyArgumentList
@attr.s
class SerGrammar:
    parse_table: dict = attr.ib()
    term_list: list = attr.ib()
    axiom: str = attr.ib()
    non_term_list: list = attr.ib()

    def build_parser(self, scanner_type: Callable, text: str):
        def get_rhs_tuple(rhs: list):
            res = []
            for x in rhs:
                try:
                    new_x = TermEnum[x]
                except KeyError:
                    new_x = NonTermEnum[x]
                res.append(new_x)
            return tuple(res)
        TermEnum = Enum('TermEnum', self.term_list)
        NonTermEnum = Enum('NonTermEnum', self.non_term_list)
        axiom = NonTermEnum[self.axiom]
        parse_table = dict()
        for lhs, rhs in self.parse_table.items():
            term, non_term = lhs
            parse_table[(TermEnum[term], NonTermEnum[non_term])] = get_rhs_tuple(rhs)
        return Parser(scanner_type, text, TermEnum, NonTermEnum, parse_table, axiom)


@attr.s
class Grammar:
    grammar_dict: Dict[Enum, Tuple[Tuple[Enum]]] = attr.ib()
    TermEnum: Enum = attr.ib()
    NonTermEnum: Enum = attr.ib()
    axiom: Enum = attr.ib()
    first_set_chain_dict: Dict = dict()

    def serialize(self):
        term_list = [x.name for x in iter(self.TermEnum)]
        non_term_list = [x.name for x in iter(self.NonTermEnum)]
        parse_table = dict()
        for lhs, rhs in self.parse_table.items():
            term, non_term = lhs
            parse_table[(term.name, non_term.name)] = tuple(x.name for x in rhs)
        return SerGrammar(parse_table, term_list, self.axiom.name, non_term_list)

    def build_parser(self, scanner_type, text):
        return Parser(scanner_type, text, self.TermEnum, self.NonTermEnum, self.parse_table, self.axiom)

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
    def __init__(self, scanner_type: Callable, text: str,
                 T: Enum, NT: Enum, table: dict,
                 axiom: Enum):
        self.compiler = Compiler(scanner_type)
        self.scanner = self.compiler.get_scanner(text)
        self.text = text
        self.T = T
        self.NT = NT
        self.table = table
        self.axiom = axiom
        self.root = NonTerminalNode(self.axiom)

    def get_token_name(self, token: Token) -> str:
        if isinstance(token, (AxiomToken, NonTerminalToken)):
            return self.compiler.get_name(token.code)
        elif isinstance(token, TerminalToken):
            return token.terminal_str
        else:
            return ""

    def token_repr(self, tok: Token):
        return f"{tok} {self.get_token_name(tok)}"

    def print_tree(self):
        self.root.print_node()

    def print_scanner(self):
        for token in self.compiler.get_scanner(self.text):
            print(self.token_repr(token))

    def parse(self, debug=False):
        stack = [self.T.END_OF_PROGRAM, self.axiom]
        a = self.next_token()
        node_stack = [self.root]
        while True:
            x = stack.pop()
            if x == self.T.END_OF_PROGRAM:
                break
            node = node_stack.pop()
            if x in self.T:
                if debug:
                    print("STACK TOP T:", x.name)

                if x == a.tag:
                    node.set_values(a, self.get_token_name(a))
                    a = self.next_token()
                else:
                    raise ParseException(a.coords)
            else:
                if debug:
                    print("STACK TOP NT:", x, ", CUR T:", self.token_repr(a))
                _tuple = (a.tag, x)

                if _tuple in self.table:
                    chain = list(self.table[_tuple])

                    while chain:
                        symbol = chain.pop()
                        if symbol in self.T:
                            new_node = TerminalNode()
                        else:
                            new_node = NonTerminalNode(symbol)
                        node.add_children(new_node)
                        node_stack.append(new_node)
                        stack.append(symbol)
                    if debug:
                        print("STACK:", stack)

                else:
                    raise ParseException(a.coords)

    def next_token(self):
        a = next(self.scanner)
        a.tag = self.get_equivalent_enum(a.tag)
        return a

    def get_equivalent_enum(self, tag):
        return getattr(self.T, tag.name)


# noinspection PyArgumentList
class GrammarParser(Parser):
    def __init__(self, text: str) -> None:
        NT = Enum('GrammarNonTerm', ['S', 'S_', 'rule', 'lhs', 'rhs', 'rhs_', 'symbols', 'symbol'])
        table = {
            (T.NON_TERMINAL, NT.S): (NT.rule, T.DOT, NT.S_),
            (T.AXIOM, NT.S): (NT.rule, T.DOT, NT.S_),
            (T.NON_TERMINAL, NT.S_): (NT.rule, T.DOT, NT.S_),
            (T.AXIOM, NT.S_): (NT.rule, T.DOT, NT.S_),
            (T.END_OF_PROGRAM, NT.S_): (),
            (T.NON_TERMINAL, NT.rule): (NT.lhs, T.ASSIGN, NT.rhs),
            (T.AXIOM, NT.rule): (NT.lhs, T.ASSIGN, NT.rhs),
            (T.NON_TERMINAL, NT.lhs): (T.NON_TERMINAL,),
            (T.AXIOM, NT.lhs): (T.AXIOM,),
            (T.NON_TERMINAL, NT.rhs): (NT.symbols, NT.rhs_),
            (T.TERMINAL, NT.rhs): (NT.symbols, NT.rhs_),
            (T.DOT, NT.rhs): (NT.symbols, NT.rhs_),
            (T.OR, NT.rhs): (NT.symbols, NT.rhs_),
            (T.DOT, NT.rhs_): (),
            (T.OR, NT.rhs_): (T.OR, NT.rhs),
            (T.NON_TERMINAL, NT.symbols): (NT.symbol, NT.symbols),
            (T.TERMINAL, NT.symbols): (NT.symbol, NT.symbols),
            (T.DOT, NT.symbols): (),
            (T.OR, NT.symbols): (),
            (T.NON_TERMINAL, NT.symbol): (T.NON_TERMINAL,),
            (T.TERMINAL, NT.symbol): (T.TERMINAL,)
        }
        axiom = NT.S
        super().__init__(GrammarScanner, text, T, NT, table, axiom)

    def transform_tree_to_grammar(self) -> Grammar:
        def handle_s(node: NonTerminalNode):
            rule, _, s_ = node.children
            lhs, _, rhs = rule.children
            lhs_child = lhs.children[0]
            lhs_child_name = lhs_child.name
            non_terminal_strs.add(lhs_child_name)
            if isinstance(lhs_child.token, AxiomToken):
                axiom_strs.add(lhs_child_name)
            rhs_list = handle_rhs(rhs)
            grammar_dict[lhs_child_name] = rhs_list
            if s_.children:
                handle_s(s_)

        def handle_rhs(node: NonTerminalNode) -> List[List[str]]:
            symbols, rhs_ = node.children
            symbols_list = handle_symbols(symbols)
            rhs_list = [symbols_list] + handle_rhs_(rhs_)
            return rhs_list

        def handle_rhs_(node: NonTerminalNode) -> List[List[str]]:
            children = node.children
            if children:
                _, rhs = children
                return handle_rhs(rhs)
            return []

        def handle_symbols(node: NonTerminalNode) -> List[str]:
            children = node.children
            if children:
                symbol, symbols = children
                symbol_child = symbol.children[0]
                symbol_child_name = symbol_child.name
                if isinstance(symbol_child.token, NonTerminalToken):
                    non_terminal_strs.add(symbol_child_name)
                else:
                    terminal_strs.add(symbol_child_name)
                return [symbol_child_name] + handle_symbols(symbols)
            return []

        def transform_rhs_list(rhs_list: Tuple[Tuple[Any]]) -> Tuple[Tuple[Any]]:
            return tuple(tuple(TermEnum[symbol]
                               if symbol in terminal_strs else
                               NonTermEnum[symbol]
                               for symbol in rhs) for rhs in rhs_list)

        def transform_dict() -> Dict[Enum, Tuple[Tuple[Enum]]]:
            transformed_dict = dict()
            for lhs, rhs_list in grammar_dict.items():
                transformed_dict[NonTermEnum[lhs]] = transform_rhs_list(rhs_list)
            return transformed_dict

        def check_undefined_non_terminals():
            for lhs, rhs_list in grammar_dict.items():
                for rhs in rhs_list:
                    for symbol in rhs:
                        if symbol in NonTermEnum and symbol not in grammar_dict:
                            raise GrammarException(f"{symbol} is undefined")

        def check_axiom_consistency():
            num_axioms = len(axiom_strs)
            if num_axioms == 0:
                raise GrammarException("No axiom defined")
            elif num_axioms > 1:
                raise GrammarException("More than one axiom are defined")

        terminal_strs, non_terminal_strs, axiom_strs = set(), set(), set()
        grammar_dict = dict()
        handle_s(self.root)
        TermEnum = Enum('TermEnum', list(terminal_strs | {'END_OF_PROGRAM'}))
        NonTermEnum = Enum('NonTermEnum', list(non_terminal_strs))

        grammar_dict = transform_dict()

        check_undefined_non_terminals()
        check_axiom_consistency()

        axiom_enum = NonTermEnum[axiom_strs.pop()]
        grammar = Grammar(grammar_dict, TermEnum, NonTermEnum, axiom_enum)
        return grammar


def calc_expr_tree(root: NonTerminalNode):
    def handle_e(node: NonTerminalNode) -> int:
        t, e1 = node.children
        val_t = handle_t(t)
        ret_e1 = handle_e1(e1)
        if ret_e1 is None:
            return val_t
        return val_t + ret_e1

    def handle_t(node: NonTerminalNode) -> int:
        f, t1 = node.children
        val_f = handle_f(f)
        ret_t1 = handle_t1(t1)
        if ret_t1 is None:
            return val_f
        return val_f * ret_t1

    def handle_f(node: NonTerminalNode) -> int:
        try:
            _, e, _ = node.children
            return handle_e(e)
        except ValueError:
            n = node.children[0]
            assert isinstance(n, TerminalNode)
            assert isinstance(n.token, NumToken)
            return n.token.num

    def handle_t1(node: NonTerminalNode) -> int:
        children = node.children
        if len(children):
            _, f, t1 = children
            val_f = handle_f(f)
            ret_t1 = handle_t1(t1)
            if ret_t1 is None:
                return val_f
            return val_f * ret_t1

    def handle_e1(node: NonTerminalNode) -> int:
        children = node.children
        if len(children):
            _, t, e1 = children
            val_t = handle_t(t)
            ret_e1 = handle_e1(e1)
            if ret_e1 is None:
                return val_t
            return val_t + ret_e1

    val = handle_e(root)
    return val
