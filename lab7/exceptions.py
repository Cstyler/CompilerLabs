from tokens import Fragment


class ParseException(Exception):

    def __init__(self, coords: Fragment) -> None:
        message = f"Syntax error at: {coords}"
        super().__init__(message)


class GrammarException(Exception):
    pass
