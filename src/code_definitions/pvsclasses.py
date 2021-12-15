from __future__ import annotations
from .expressions import *
from copy import deepcopy


# TODO: Function/loop to actually parse out a python file into all this stuff


class AbstractBlock:
    keyword = kwposs

    def __init__(self, content: list[Expression]) -> None:
        if all(string_check := [isinstance(line, str) for line in content]):
            line_counter = 0
            content = [
                Expression(line, line_counter := line_counter + 1) \
                if isinstance(line, str) else line for line in content
            ]
        elif any(string_check):
            for i in range(0, len(content)):
                if string_check[i]:
                    content[i] = Expression(content[i], content[i-1].line_num)
        
        
        self._content: list[Expression] = content
        self.head: Expression = content[0]
        self.lines: list[Expression] = content[1:]
        self.regex_pattern = self.regex(self.keyword)
        self.metadata = self.get_info()
        self.nested_blocks: dict = dict()  # use the relative line number as the key

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def regex(keyword: str) -> re.Pattern:
        print("NamedBlock Regex is being requested")
        return re.compile(rf"^[\t ]*(?P<keyword>{keyword}).*$")

    def get_info(self) -> dict:
        # print("Keyword:", self.keyword)
        match = re.match(self.regex_pattern, self.head.line)
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
        if argstr := self.metadata.get("args", ""):
            self.args: list[Argument] = [Argument(arg) for arg in argstr.split(',')]  # argh
        else: 
            self.args: list[Argument] = []
            
        self.is_generator: bool = any(line.line.strip().startswith("yield") for line in self.lines)
        self.returns: Expression = self.lines[-1]
        assert not self.metadata.get('async', False), "This should be a Coroutine object!"

    @staticmethod
    def regex(keyword: str) -> re.Pattern:
        """Searches header for the general function info"""
        # TODO: support return type hints, gfdi
        return re.compile(rf"^\s*(?P<async>async )?(?P<keyword>{keyword}) (?P<name>\w+)?\((?P<args>[\w:,= ]*)\):\s*$", re.I)

    
    def get_info(self) -> dict:
        groups = super().get_info()
        groups['async'] = bool(groups['async'])
        return groups

    @classmethod
    def typecast(cls: type, inst: AnyFunc) -> AnyFunc:
        """
        typecast(cls: type, inst: AnyFunc) -> AnyFunc
        This class method casts an instance of any Function to the class it is called from.
        It does this by creating an empty `cls`, then it sets that object's __dict__ to the __dict__ of inst. 
        This somehow just works, and the resulting object even has the right methods for its class.
        Example:

            myfunc: Function
            myfunc.keyword = "async def" 
            mycoro = Coroutine.typecast(myfunc)

        It is not recommended to call this directly unless you intend to sort out all the things that
        are different between normal instances your initial class and normal instances of the casted class
        Instead, use predefined class conversions that utilise this:

            myclass: Class
            myfunc: Function
            mymeth = myfunc.to_meth(method_of=myclass)
        """
        new_obj = inst.__new__(cls)  # could be cls.__new__(cls) too
        new_obj.__dict__ = deepcopy(inst.__dict__)  # magically works, don't question why
        del inst  # no longer needed since its attributes were deepcopied, cleans up space
        return new_obj

    def _switch_def_type(self, async_def=False) -> None:
        if async_def:
            assert not self.metadata.get("async", ""), f"{self} is already async"
            setattr(self, 'keyword', 'async def')
            setattr(self.head, 'line', self.head.line.replace("async def", "def", count=1))
        else:
            assert newself.metadata.get("async", ""), f"{self} is already sync"
            setattr(self, 'keyword', 'def')
            setattr(self.head, 'line', self.head.line.replace("async def", "def", count=1))

    def to_func(self) -> Function:
        """Converts Coroutine, Method, or CoroMethod to Function

        Raises:
            TypeError: If self is not one of the above

        Returns:
            Function -- has all properties of self that are not specific to 
            the type of block function it is coverting from.
            Things like changing "async def" to "def" are handled here.
        """
        if isinstance(self, Function):
            # No conversion, can be used as an ensure
            return self

        elif isinstance(self, Method):
            # Sync method to sync function
            newself: Function = Function.typecast(self)
            delattr(newself, 'method_of')
            delattr(newself, 'method_type')
            
        elif isinstance(self, Coroutine):
            # Async function to sync function
            newself: Function = Function.typecast(self)
            newself._switch_def_type(False)
        
        elif isinstance(self, CoroMethod):
            # Async method to sync function
            # Convert to a sync method first
            intermediate_self: Method = self.to_meth()
            return intermediate_self.to_func()
        
        else: 
            raise TypeError(f"Cannot convert {type(self)} to Function!")

        newself.metadata = newself.get_info()
        return newself

    def to_coro(self) -> Coroutine:
        """Converts Function, Method, or CoroMethod to Coroutine

        Raises:
            TypeError: If self is not a Function Block type

        Returns:
            Coroutine -- has all properties of self that are not specific to 
            the type of block function it is coverting from.
            Things like changing "def" to "async def" are handled here.
        """
        
        if isinstance(self, Coroutine):
            # No conversion, can be used as an ensure
            return self

        elif isinstance(self, Function):
            # Sync function to async function
            newself: Coroutine = Coroutine.typecast(self)
            newself._switch_def_type(async_def=True)

        elif isinstance(self, CoroMethod):
            # Async method to async function
            newself: Coroutine = Coroutine.typecast(self)
            delattr(newself, 'method_of')
            delattr(newself, 'method_type')

        elif isinstance(self, Method):
            # Sync method to async function
            # convert to a sync function first
            intermediate_self: Function = self.to_func()
            return intermediate_self.to_coro()
        
        else: 
            raise TypeError(f"Cannot convert {type(self)} to Function!")

        setattr(newself, 'metadata', newself.get_info())
        return newself

    def to_meth(self, method_of: Class = None, method_type: str = "object") -> Method:
        """Converts Function, Coroutine, or CoroMethod to Method

        Raises:
            TypeError: If self is not a Function Block type

        Returns:
            Method -- has all properties of self that are not specific to 
            the type of block function it is coverting from.
            If converting from a non-method, you will need to provide
            the class that the new method belongs to, as well as
            what type of method it is (static, class, object).
            Things like changing "def" to "async def" are handled here.
        """
        # TODO: Class.add_method(meth) when classes are done
        isfunc = isinstance(self, Function)
        iscoro = isinstance(self, Coroutine)
        ismeth = isinstance(self, Method)
        iscmth = isinstance(self, CoroMethod)

        if ismeth:
            # No conversion needed, can be used as an ensure
            if any((method_of, method_type)): 
                raise ValueError(
                    "Method.to_cmth() is not for updating method membership or type!\n"
                    "Please use Method.update() instead."
                )
        
            return self
        
        elif isfunc:
            # Sync function to sync method
            newself: Method = Method.typecast(self)
            
        elif iscoro:
            # Async function to sync method
            # Convert async to sync first
            intermediate_self: Function = self.to_func()
            intermediate_self._switch_def_type(async_def=False)
            return intermediate_self.to_meth(method_of=method_of, method_type=method_type)

        elif iscmth:
            # Async method to sync method
            newself: Method = Method.typecast(self)
            newself._switch_def_type(async_def=False)
            
        else:
            # dafuq is dis
            raise TypeError(f"Cannot convert {type(self)} to Function!")
        
        # if it didn't have these attributes, add them. they must exist
        if not iscmth:
            assert method_of is not None, f"Must provide Class to make {self.name} a method of!"
            assert method_type is not None, f"Must provide method type of {self.name}!"
            setattr(newself, 'method_type', method_type)
            setattr(newself, 'method_of', method_of)

        # if it does, and we are trying to one or both them
        elif iscmth:
            if method_of is not None:
                setattr(newself, 'method_of', method_of)
            if method_type is not None:
                setattr(newself, 'method_type', method_type)

        # update metadata
        setattr(newself, 'metadata', newself.get_info())
        return newself

    def to_cmth(self, method_of: Class = None, method_type: str = "object") -> CoroMethod:
        """Converts Function, Coroutine, or Method to CoroMethod

        Raises:
            TypeError: If self is not a Function Block type

        Returns:
            CoroMethod -- has all properties of self that are not specific to 
            the type of block function it is coverting from.
            If converting from a non-method, you will need to provide
            the class that the new method belongs to, as well as
            what type of method it is (static, class, object).
            Things like changing "def" to "async def" are handled here.
        """
        # TODO: Class.add_method(meth) when classes are done
        isfunc = isinstance(self, Function)
        iscoro = isinstance(self, Coroutine)
        ismeth = isinstance(self, Method)
        iscmth = isinstance(self, CoroMethod)

        if iscmth:
            # No conversion needed, can be used as an ensure
            if any((method_of, method_type)): 
                raise ValueError(
                    "CoroMethod.to_coromethod() is not for updating method membership or type!\n"
                    "Please use CoroMethod.update() instead."
                )
        
            return self
        
        elif isfunc:
            # Sync function to async method
            newself: Method = Method.typecast(self)
            
        elif iscoro:
            # Sync function to async method
            # Convert sync to async first
            intermediate_self: Coroutine = self.to_coro()
            intermediate_self._switch_def_type(async_def=True)
            return intermediate_self.to_cmth(method_of=method_of, method_type=method_type)

        elif ismeth:
            # Sync method to async method
            newself: CoroMethod = CoroMethod.typecast(self)
            newself._switch_def_type(async_def=True)
            
        else:
            # dafuq is dis
            raise TypeError(f"Cannot convert {type(self)} to Function!")

        # if it didn't have these attributes, add them. they must exist
        if not ismeth:
            assert method_of is not None, f"Must provide Class to make {self.name} a method of!"
            assert method_type is not None, f"Must provide method type of {self.name}!"
            setattr(newself, 'method_type', method_type)
            setattr(newself, 'method_of', method_of)

        # if it does, and we are trying to one or both them
        elif ismeth:
            if method_of is not None:
                setattr(newself, 'method_of', method_of)
            if method_type is not None:
                setattr(newself, 'method_type', method_type)

        # update metadata
        setattr(newself, 'metadata', newself.get_info())
        return newself


class Coroutine(Function):
    keyword = "async def"


class Method(Function):
    def __init__(self, content: list[Expression], method_type: str = "object", method_of: str = None) -> None:
        super().__init__(content)
        self.method_type: str = method_type  # whether the method is static or applies to the class or class instance
        assert method_of is not None, "Must provide Class to make method of!"
        self.method_of = method_of

class CoroMethod(Coroutine, Method):
    pass


AnyFunc = Function | Coroutine | Method | CoroMethod


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