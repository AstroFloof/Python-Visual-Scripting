import re
from keyword import kwlist, softkwlist 


kwposs = ' |'.join(kwlist + softkwlist)


getwspc = re.compile(r"^(?P<whitespace>[\t ]*).*$", re.I)
getkwds = re.compile(rf"^(?P<keyword>({kwposs})*)")
funcinfo = re.compile(r"^\s*(?P<isasync>async )?def (?P<name>\w+)?\((?P<args>[\w:,= ]*)\):\s*$", re.I)


general_line_re = re.compile(rf"""^([\t ]*)   # get amount of preceeding whitespace, so that we can determine block membership
                                  ({kwposs}?) # get whether this is the start of a block, and what it is
                                  ( )         # space between kw and name
                                  (\w+)       # name if function
                                  \((.+)\)    # args, handle later
                                  :\s*$       # end of line         """,   
                                  flags=re.I | re.X)


class Expression(str):
    
    def __init__(self, line: str, positional: tuple[int, int]) -> None:
        self._indentation: str = re.match(getwspc, line).groupdict()['whitespace']
        tabs, spaces = '\t' in self._indentation, '' in self._indentation
        if tabs and spaces:
            raise SyntaxError("Inconsistent use of tabs and spaces!")

        self.indent_type: str = '\t' if tabs else ' '
