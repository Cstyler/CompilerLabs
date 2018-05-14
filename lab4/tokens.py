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
    FUNCTION_NAME = auto()
    SUB_KEYWORD = auto()
    IF_KEYWORD = auto()
    UNLESS_KEYWORD = auto()
    END_OF_PROGRAM = auto()


class Token(ABC):
    def __init__(self, tag: DomainTag, starting: Position, following: Position):
        self._tag = tag
        self._coords = Fragment(starting, following)

    def __str__(self):
        return f'{self._tag} {str(self._coords)}:'


class IdentToken(Token):
    def __init__(self, code: int, starting: Position, following: Position):
        super().__init__(DomainTag.IDENT, starting, following)
        self._code = code

    @property
    def code(self):
        return self._code


class FunctionNameToken(Token):
    def __init__(self, code: int, starting: Position, following: Position):
        super().__init__(DomainTag.FUNCTION_NAME, starting, following)
        self._code = code

    @property
    def code(self):
        return self._code


class KeywordToken(Token):
    domain_tags = {DomainTag.SUB_KEYWORD, DomainTag.IF_KEYWORD, DomainTag.UNLESS_KEYWORD}

    def __init__(self, tag: DomainTag, starting: Position, following: Position):
        assert tag in KeywordToken.domain_tags
        super().__init__(tag, starting, following)


class SpecToken(Token):
    domain_tags = {DomainTag.END_OF_PROGRAM}

    def __init__(self, tag: DomainTag, starting: Position, following: Position):
        assert tag in SpecToken.domain_tags
        super().__init__(tag, starting, following)
