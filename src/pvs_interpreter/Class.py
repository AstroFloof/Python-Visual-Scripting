from __future__ import annotations
from .Blocks import *

class Class(NamedBlock):
    keyword = "class"

    def __init__(self, content: list[Expression]) -> None:  # TODO: this is incomplete
        super().__init__(content)
        class_variables: list[Expression]
        self.methods: list[Method]
