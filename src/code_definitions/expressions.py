import re
from keyword import kwlist, softkwlist 

# TODO: Move this shit out to staticmethods in pvsclasses
kwposs = ' |'.join(list(kwlist) + list(softkwlist))
getwspc = re.compile(r"^(?P<whitespace>[\t ]*).*$", re.I)
getkwds = re.compile(rf"^(?P<keyword>({kwposs})*)")
funcinfo = re.compile(r"^\s*(?P<isasync>async )?def (?P<name>\w+)?\((?P<args>[\w:,= ]*)\):\s*$", re.I)


general_line_re = re.compile(rf"""^([\t ]*)   # get amount of preceeding whitespace, for determininh block membership
                                  ({kwposs}?) # get whether this is the start of a block, and what it is
                                  ([ ])       # space between kw and name
                                  (\w+)       # name if function
                                  \((.+)\)    # args, handle later
                                  :\s*$       # end of line         """,
                             flags=re.I | re.X)


class Expression(str):
    
    def __init__(self, line: str, line_num: int) -> None:  # TODO: Expression types e.g. variable set, function call
        self._indentation: str = re.match(getwspc, line).groupdict()['whitespace']
        uses_tabs, uses_spaces = '\t' in self._indentation, '' in self._indentation
        if uses_tabs and uses_spaces:
            raise SyntaxError("Inconsistent use of tabs and spaces!")

        self.indent_type: str = '\t' if uses_tabs else ' '
        self.line: int = line_num
