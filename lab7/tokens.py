from enum import Enum, auto
from position import Position
from abc import ABC


class Fragment:
    def __init__(self, starting: Position, ending: Position):
        self._starting = starting
        self._ending = ending

    def __str__(self) -> str:
        return f"{self._starting} - {self._ending}"


class T(Enum):
    NON_TERMINAL = auto()
    TERMINAL = auto()
    DOT = auto()
    OR = auto()
    ASSIGN = auto()
    AXIOM = auto()
    END_OF_PROGRAM = auto()


class CalcTag(Enum):
    n = auto()
    PLUS = auto()
    MUL = auto()
    LPAREN = auto()
    RPAREN = auto()
    END_OF_PROGRAM = auto()


class Token(ABC):
    def __init__(self, tag: Enum, starting: Position, following: Position):
        self._tag = tag
        self._coords = Fragment(starting, following)

    def __str__(self):
        return f'{self._tag} {str(self._coords)}:'

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value: Enum):
        self._tag = value

    @property
    def coords(self):
        return self._coords


class NonTerminalToken(Token):
    def __init__(self, code: int, starting: Position, following: Position):
        super().__init__(T.NON_TERMINAL, starting, following)
        self._code = code

    @property
    def code(self):
        return self._code


class TerminalToken(Token):
    def __init__(self, terminal_str: str, starting: Position, following: Position):
        super().__init__(T.TERMINAL, starting, following)
        self._terminal_str = terminal_str

    @property
    def terminal_str(self):
        return self._terminal_str


class SpecToken(Token):
    domain_tags = {T.END_OF_PROGRAM, T.ASSIGN, T.DOT, T.OR}

    def __init__(self, tag: Enum, starting: Position, following: Position):
        assert tag in self.domain_tags
        super().__init__(tag, starting, following)


class AxiomToken(Token):
    def __init__(self, code: int, starting: Position, following: Position):
        super().__init__(T.AXIOM, starting, following)
        self._code = code

    @property
    def code(self):
        return self._code


class NumToken(Token):
    def __init__(self, num: int, starting: Position, following: Position):
        super().__init__(CalcTag.n, starting, following)
        self._num = num

    @property
    def num(self):
        return self._num

    def __str__(self):
        return f"{super().__str__()} {str(self._num)}"


class CalcSpecToken(Token):
    domain_tags = {CalcTag.LPAREN, CalcTag.RPAREN, CalcTag.MUL, CalcTag.PLUS, CalcTag.END_OF_PROGRAM}

    def __init__(self, tag: CalcTag, starting: Position, following: Position):
        assert tag in self.domain_tags
        super().__init__(tag, starting, following)
