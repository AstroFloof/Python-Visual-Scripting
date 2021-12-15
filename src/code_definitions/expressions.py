import re
from keyword import kwlist, softkwlist 


# TODO: Move this shit out to staticmethods in pvsclasses
kwposs = ' |'.join(list(kwlist) + list(softkwlist))
getwspc = re.compile(r"^(?P<whitespace>[\t ]*).*$", re.I)
getkwds = re.compile(rf"^(?P<keyword>({kwposs})*)")


general_line_re = re.compile(rf"""^([\t ]*)   # get amount of preceeding whitespace, for determininh block membership
                                  ({kwposs}?) # get whether this is the start of a block, and what it is
                                  ([ ])       # space between kw and name
                                  (\w+)       # name if function
                                  \((.+)\)    # args, handle later
                                  :\s*$       # end of line         """,
                             flags=re.I | re.X)


class Expression:
    
    def __init__(self, line: str, line_num: int) -> None:  # TODO: Expression types e.g. variable set, function call
        self._indentation: str = re.match(getwspc, line).groupdict()['whitespace']
        uses_tabs, uses_spaces = '\t' in self._indentation, ' ' in self._indentation
        if uses_tabs and uses_spaces:
            raise SyntaxError("Inconsistent use of tabs and spaces!")

        self.indent_type: str = '\t' if uses_tabs else ' '
        self.line: str = line
        self.line_num: int = line_num

    def __str__(self):
        return str(self.__dict__)


AVTC = r"[\w|_\s^\v]+"  # All Valid Typing Characters
ST = r"[\s^\v]"  # Space or Tab - all whitespace minus vertical ones
def OWO(operator: str): return rf"{ST}?{operator}{ST}?"  # Optionally Whitespaced Operator


class Argument:

    REGEX = re.compile(
        rf"""
        ^(?P<name>\w+)
        (?P<has_typehint>{OWO(':')}?)?
        (?(has_typehint)(?P<type>{AVTC})?|)?
        (?P<has_default>{OWO('=')})?
        (?(has_default)(?P<default>{AVTC})?|)?$""",
        flags=re.I | re.X)

    def __init__(self, raw: str):
        match = re.match(self.REGEX, raw.strip())
        if match is None:
            assert raw, "This argument is empty!"
            raise ValueError(f"This argument is invalid!\n{raw}")

        result = match.groupdict()
        self.name: str = result.get('name', '').strip()
        if result.get('has_typehint', False):
            self.type: list[str] = [union_member.strip() for union_member in result.get('type', '').split("|")]
        else: 
            self.type = None
        
        if result.get('has_default', False):
            self.default: str = result.get('default', '')
        else:
            self.default = None
