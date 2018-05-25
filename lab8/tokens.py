from enum import Enum, auto
from typing import List

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
    MUL = auto()
    PLUS = auto()
    QUEST_MARK = auto()
    OR = auto()
    ASSIGN = auto()
    LPAREN = auto()
    RPAREN = auto()
    DOT = auto()
    END_OF_PROGRAM = auto()


class Token(ABC):
    def __init__(self, tag: Enum, starting: Position, following: Position):
        self._tag = tag
        self._coords = Fragment(starting, following)

    def __str__(self):
        return f'{self._tag} {str(self._coords)}:'

    # def __repr__(self):
    #     return f'{self._tag}'

    def has_tag(self, tag: Enum):
        return self.tag == tag

    def has_one_of_tags(self, *tags: Enum):
        return any(self.tag == tag for tag in tags)

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
    domain_tags = {T.END_OF_PROGRAM, T.LPAREN, T.RPAREN, T.ASSIGN, T.MUL, T.PLUS, T.QUEST_MARK, T.OR, T.DOT}

    def __init__(self, tag: Enum, starting: Position, following: Position):
        assert tag in self.domain_tags
        super().__init__(tag, starting, following)
