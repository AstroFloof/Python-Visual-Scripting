from __future__ import annotations
from .Functions import *  # also gets Expressions, Blocks, and Class
from .ControlFlow import *

print(annotations)

# TODO: Function/loop to actually parse out a python file into all this stuff


'''
# print(re.compile(rf"^[\t ]*(?P<keyword>{kwposs})(?P<name>\w+).*:$"))
print("make expr")
myexpr = Expression("def function(*args, **kwargs) -> returns:", 1)
print("make generic named block")
myblock = NamedBlock([myexpr])
print("make function")
myfunc = Function([myexpr])
'''