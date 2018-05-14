import functools
from typing import Union


@functools.total_ordering
class Position:
    def __init__(self, text: str, line: int, pos: int, index: int):
        self._text = text
        self._line = line
        self._pos = pos
        self._index = index

    @classmethod
    def default_position(cls, text: str):
        return cls(text, 1, 1, 0)

    @property
    def line(self) -> int:
        return self._line

    @property
    def pos(self) -> int:
        return self._pos

    @property
    def index(self) -> int:
        return self._index

    def __lt__(self, other) -> bool:
        return self.index < other.index

    def __eq__(self, other) -> bool:
        return self.index == other.index

    def __str__(self) -> str:
        return f'({self._line}, {self._pos})'

    @property
    def cp(self) -> Union[int, str]:
        return -1 if self._index == len(self._text) else self._text[self._index]

    @property
    def is_white_space(self) -> bool:
        cp = self.cp
        return cp != -1 and cp.isspace()

    @property
    def is_letter(self) -> bool:
        cp = self.cp
        return cp != -1 and (cp.isalpha() or cp == '_')

    @property
    def is_letter_or_digit(self) -> bool:
        cp = self.cp
        return cp != -1 and (cp.isalnum() or cp == '_')

    @property
    def is_digit(self) -> bool:
        cp = self.cp
        return cp != -1 and cp.isdigit()

    @property
    def is_new_line(self) -> bool:
        return self.cp in (-1, '\n')

    @property
    def is_terminal_symbol(self) -> bool:
        return not self.is_white_space and self.cp not in {'=', '|', '.'}

    def __next__(self):
        line, pos, index = self._line, self._pos, self._index
        if index < len(self._text):
            if self.is_new_line:
                line += 1
                pos = 1
            else:
                pos += 1
            index += 1
        return Position(self._text, line, pos, index)
