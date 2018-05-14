from enum import Enum, auto
from position import Position
from abc import ABC


class Fragment:
    def __init__(self, starting: Position, ending: Position):
        self._starting = starting
        self._ending = ending

    def __str__(self) -> str:
        return f"{self._starting} - {self._ending}"


class DomainTag(Enum):
    IDENT = auto()
    NUMBER = auto()
    IF_KEYWORD = auto()
    THEN_KEYWORD = auto()
    ELSE_KEYWORD = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMENT = auto()
    SPACE = auto()
    END_OF_PROGRAM = auto()


class Token(ABC):
    def __init__(self, tag: DomainTag, starting: Position, following: Position):
        self.tag = tag
        self.coords = Fragment(starting, following)
        self.repr = starting.get_substr(following)

    def __str__(self):
        return f"{self.tag} {self.coords}: {self.repr}"