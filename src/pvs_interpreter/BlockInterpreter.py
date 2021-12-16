from __future__ import annotations
from .Functions import *  # also gets Expressions, Blocks, and Class
from .ControlFlow import *


# TODO: Function/loop to actually parse out a python file into all this stuff
BLOCKTYPES = [
    Function, Class, Method, Match, MatchCase, If, Elif, Else, 
    While, For
]
BTKEYWORDS = {T.keyword: T for T in BLOCKTYPES}


class File(NamedBlock):
    
    def __init__(self, filename: str):
        content: list[Expression] = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                content.append(Expression(line, len(content) + 1))
        super().__init__(content)



'''
# print(re.compile(rf"^[\t ]*(?P<keyword>{kwposs})(?P<name>\w+).*:$"))
print("make expr")
myexpr = Expression("def function(*args, **kwargs) -> returns:", 1)
print("make generic named block")
myblock = NamedBlock([myexpr])
print("make function")
myfunc = Function([myexpr])
'''