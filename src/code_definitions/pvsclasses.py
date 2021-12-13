from .expressions import *

# TODO: Function/loop to actually parse out a python file into all this stuff


class AbstractBlock:
    keyword = ""

    def __init__(self, content: list[Expression]) -> None:
        self._content: list[Expression] = content
        self.head: Expression = content[0]
        self.lines: list[Expression] = content[1:]


class NamedBlock(AbstractBlock):
    keyword = ""

    def __init__(self, content: list[Expression]) -> None:
        super().__init__(content)
        self.regex_pattern = self.regex(self.keyword)
        self.metadata = self.get_info()
        self.name = self.metadata['name']

    @staticmethod
    def regex(keyword: str) -> re.Pattern:
        return re.compile(rf"^[\t ]*{keyword} (?P<name>\w+).*:$")

    def get_info(self) -> dict:
        return re.match(self.regex_pattern, self.head).groupdict()


class Function(NamedBlock):
    keyword = "def"

    def __init__(self, block: NamedBlock) -> None:
        super().__init__(block._content)
        self.args: Expression = self.head
        self.returns: Expression = self.lines[-1]


class Coroutine(Function):
    keyword = "async def"


class Method(Function):
    def __init__(self, block: NamedBlock, method_type: str = "object") -> None:
        super().__init__(block)
        self.type: str = method_type  # whether the method is static or applies to the class or class instance


class CoroMethod(Coroutine, Method):
    pass


class Class(NamedBlock):
    keyword = "class"

    def __init__(self, block: NamedBlock) -> None:  # TODO: this is incomplete
        self.block = block
        del block
        super().__init__(self.block.lines)
        class_variables: list[Expression]
        self.methods: list[Method]


class If(AbstractBlock):  # TODO: if stuff
    keyword = "if"


class Elif(If):
    keyword = "elif"


class Else(AbstractBlock):
    keyword = "else"


class Conditional(AbstractBlock):
    keyword = "if"

    def __init__(self, block: AbstractBlock) -> None:
        self.block = block
        super().__init__(self.block.lines)
        self.If: tuple[Expression, AbstractBlock]
        self.Else_Ifs: list[Expression]
        self.Else: Expression


class MatchCase:  # TODO
    keyword = "case"


class Match(AbstractBlock):  # TODO
    pass


class Loop(AbstractBlock):  # TODO
    pass
