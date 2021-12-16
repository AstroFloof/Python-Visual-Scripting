from __future__ import annotations
from .Blocks import *


class File(NamedBlock):
    pass  # TODO: no


class Conditional(AbstractBlock):
    keyword = "if |elif |else |while "

    def __init__(self, block: AbstractBlock) -> None:
        self.block = block
        super().__init__(self.block.lines)
        self.if_condition: tuple[Expression, AbstractBlock]
        self.elifs: list[Expression]
        self.Else: Expression


class If(AbstractBlock):  # TODO: if stuff
    keyword = "if"


class Elif(If):
    keyword = "elif"


class Else(AbstractBlock):
    keyword = "else"


class MatchCase:  # TODO
    keyword = "case"


class Match(AbstractBlock):  # TODO
    pass


class Loop(AbstractBlock):  # TODO
    pass
