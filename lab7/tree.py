import abc
from enum import Enum
from typing import List

from tokens import Token


class Node(abc.ABC):
    @abc.abstractmethod
    def print_node(self, node):
        pass


class TerminalNode(Node):
    def set_values(self, token: Token, name: str):
        self.token = token
        self.name = name

    def __str__(self):
        if self.name:
            return f"{self.token} {self.name}"
        else:
            return str(self.token)

    __repr__ = __str__

    def print_node(self, ident: str = ""):
        print(f"{ident}{str(self)}")


class NonTerminalNode(Node):
    children: List[Node]

    def __init__(self, nt_tag: Enum) -> None:
        self.children = []
        self.nt_tag = nt_tag

    def add_children(self, child: Node):
        self.children.insert(0, child)

    def __str__(self):
        return str(self.nt_tag.name)

    __repr__ = __str__

    def print_node(self, indent: str = ""):
        print(indent + str(self))
        new_indent = f"{indent}|"
        for child in self.children:
            child.print_node(new_indent)
