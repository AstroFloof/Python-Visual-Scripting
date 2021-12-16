from __future__ import annotations
from .Blocks import *


class Conditional(AbstractBlock):
    keyword = "if |elif |else |while "

    def __init__(self, content: list[Expression]) -> None:
        super().__init__(content)
        self.condition: Expression = content[0].replace(self.keyword)
        self.body: list[Expression] = content[1:]

        # these two are mutually exclusive, so a chain of if-elif--elif-else
        # is structured like this If If.Elif If.Elif.Elif If.Elif.Elif.Else
        self.elif_: Elif = None  # elifs will chain
        self.else_: Else = None  # must not have both
        

class If(Conditional):  # TODO
    keyword = "if"


class Elif(If):
    keyword = "elif"


class Else(AbstractBlock):
    keyword = "else"


class MatchCase:  # TODO
    keyword = "case"


class Match(AbstractBlock):  # TODO
    keyword = "match"


class Loop(AbstractBlock):  # TODO
    pass


class While(Loop, Conditional):
    keyword = "while"


class For(Loop):
    keyword = "for"