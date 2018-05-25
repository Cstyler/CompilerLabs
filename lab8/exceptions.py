from tokens import Fragment, Enum


class ParseException(Exception):

    def __init__(self, coords: Fragment, *expected_tags: Enum) -> None:
        message = f"Syntax error at: {coords}. Expected tags: {expected_tags}"
        super().__init__(message)


class GrammarException(Exception):
    pass
