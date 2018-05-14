from scanner import GrammarScanner
from position import Position


class Message:
    def __init__(self, is_error: bool, text: str, coord: Position):
        self._is_error = is_error
        self._text = text
        self._coord = coord

    def __str__(self):
        return f'{"Error" if self._is_error else "Warning"}:{self._coord}: {self._text}'


class Compiler:
    def __init__(self):
        self._messages = []
        self._name_codes = dict()
        self._names = []

    def get_scanner(self, program: str) -> GrammarScanner:
        return GrammarScanner(program, self)

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
