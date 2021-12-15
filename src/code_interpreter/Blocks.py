from .expressions import *


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
