from __future__ import annotations
from .expressions import *

# TODO: Function/loop to actually parse out a python file into all this stuff


class AbstractBlock:
    keyword = kwposs

    def __init__(self, content: list[Expression]) -> None:
        self._content: list[Expression] = content
        self.head: Expression = content[0]
        self.lines: list[Expression] = content[1:]
        self.regex_pattern = self.regex(self.keyword)
        self.metadata = self.get_info()
        self.keyword = self.metadata['keyword']
        self.nested_blocks: dict = dict()  # use the relative line number as the key

    @staticmethod
    def regex(keyword: str) -> re.Pattern:
        print("NamedBlock Regex is being requested")
        return re.compile(rf"^[\t ]*(?P<keyword>{keyword}).*$")

    def get_info(self) -> dict:
        # print("Keyword:", self.keyword)
        match = re.match(self.regex_pattern, str(self.head))
        print(match)
        return match.groupdict()

    # TODO: modify_lines(blank deletes), serialize(), add_line(optional insertion position), add_block(), remove_block()


class NamedBlock(AbstractBlock):

    def __init__(self, content: list[Expression]) -> None:
        super().__init__(content)
        self.name: str = self.metadata['name']

    @staticmethod
    def regex(keyword: str) -> re.Pattern:
        print("NamedBlock Regex is being requested")
        return re.compile(rf"^[\t ]*(?P<keyword>{keyword})(?P<name>\w+).*:$")

    # TODO: same as above, as well as name changing


class File(NamedBlock):
    pass  # TODO: no


class Function(NamedBlock):
    keyword = "def"
    '''
    def __new__(cls, block: NamedBlock) -> Coroutine | Function:
        if block.metadata['async']:
            return Coroutine(block)
        return super().__init__(block._content)'''

    def __init__(self, content: list[Expression]) -> None:
        super().__init__(content)
        self.args: list[Argument] = [Argument(arg) for arg in self.metadata.get("args", "").split(',')]  # argh
        self.is_generator: bool = any(line.line.strip().startswith("yield") for line in self.lines)
        self.returns: Expression = self.lines[-1]
        assert not self.metadata.get('async', False), "This should be a Coroutine object!"

    @staticmethod
    def regex(keyword: str) -> re.Pattern:
        """Searches header for the general function info"""
        # TODO: support return type hints, gfdi
        return re.compile(r"^\s*(?P<async>async )?def (?P<name>\w+)?\((?P<args>[\w:,= ]*)\):\s*$", re.I)

    
    def get_info(self) -> dict:
        groups = super().get_info()
        groups['async'] = bool(groups['async'])
        return groups

    # TODO: make a way to convert between function types
    @classmethod
    def typecast(cls, inst):
        new_obj = inst.__new__(Function)
        new_obj.__dict__ = inst.__dict__  # magically works, don't question why



class Coroutine(Function):
    keyword = "async def"


class Method(Function):
    def __init__(self, content: list[Expression], method_type: str = "object") -> None:
        super().__init__(content)
        self.method_type: str = method_type  # whether the method is static or applies to the class or class instance


class CoroMethod(Coroutine, Method):
    pass


class Class(NamedBlock):
    keyword = "class"

    def __init__(self, content: list[Expression]) -> None:  # TODO: this is incomplete
        super().__init__(content)
        class_variables: list[Expression]
        self.methods: list[Method]


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

'''
# print(re.compile(rf"^[\t ]*(?P<keyword>{kwposs})(?P<name>\w+).*:$"))
print("make expr")
myexpr = Expression("def function(*args, **kwargs) -> returns:", 1)
print("make generic named block")
myblock = NamedBlock([myexpr])
print("make function")
myfunc = Function([myexpr])
'''