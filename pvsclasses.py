

class Expression(str):
    pass


class AbstractBlock:

    def __init__(self, keyword: str, content: list[Expression]):
        self.keyword: str = keyword
        self._content: list[Expression] = content
        self.head: Expression = content[0]
        self.lines: list[Expression] = content[1:]

class NamedBlock(AbstractBlock):

    def __init__(self, content: list[Expression]):
        super().__init__(content)
        self.name = self.head.removeprefix(self.keyword + " ")


class Function(NamedBlock):

    def __init__(self, block: NamedBlock):
        super().__init__(block.name, block._content)
        self.args: Expression = self.head
        self.returns: Expression = self.lines[-1]


class Method(Function):

    def __init__(self, block: AbstractBlock, method_type: str = 'object'):
        super().__init__(block)
        self.type: str = method_type  # whether the method is static or applies to the class or class instance


class Class(AbstractBlock):

    def __init__(self, block: AbstractBlock):
        self.block = block
        del block
        super().__init__(self.block.lines)
        class_variables: list[Expression]
        self.methods: list[Method]


class Conditional(AbstractBlock):

    def __init__(self, block: AbstractBlock):
        self.block = block
        super().__init__(self.block.lines)
        self.If: tuple[Expression, AbstractBlock]
        self.Else_Ifs: list[Expression]
        self.Else: Expression


class Case:
    pass


class Match(AbstractBlock):
    pass


class Loop(AbstractBlock):
    pass
