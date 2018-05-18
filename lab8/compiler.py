from collections import Iterable, Callable
from position import Position
import attr


@attr.s
class Message:
    _is_error: bool = attr.ib()
    _text: str = attr.ib()
    _coord: Position = attr.ib()

    def __str__(self):
        return f'{"Error" if self._is_error else "Warning"}:{self._coord}: {self._text}'


@attr.s
class Compiler:
    scanner: Callable = attr.ib()
    _messages = list()
    _names = list()
    _name_codes = dict()

    def get_scanner(self, program: str) -> Iterable:
        return self.scanner(program, self)

    def add_name(self, name: str) -> int:
        if name not in self._name_codes:
            code = len(self._names)
            self._name_codes[name] = code
            self._names.append(name)
            return code
        else:
            return self._name_codes[name]

    def get_name(self, code: int) -> str:
        if code is not None:
            return self._names[code]
        return str()

    def add_message(self, is_err: bool, text: str, coord: Position):
        self._messages.append(Message(is_err, text, coord))

    def output_messages(self):
        for message in self._messages:
            print(message)
