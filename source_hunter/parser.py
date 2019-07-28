import re
from typing import List
from abc import ABC, abstractmethod


class BaseParser(ABC):
    def __init__(self, lang="python"):
        self.lang = lang

    @abstractmethod
    def parse_children_modules(content_lines: List[str]):
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def get_calling_func(parent_fnode, child_fnode, child_class_or_func: str):
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def get_calling_class(parent_fnode, child_fnode, child_class_or_func: str):
        raise NotImplementedError("This method is not implemented")


class PythonParser(BaseParser):
    @staticmethod
    def parse_children_modules(content_lines: List[str]):
        import_patterns = []
        import_patterns.append(re.compile("import (.*)"))
        import_patterns.append(re.compile("from (.*) import (.*)"))
        modules = []
        for line in content_lines:
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    if len(groups) > 1:  # pattern: from abc import Abc
                        for module_name in groups[1].split(","):
                            modules.append(".".join([groups[0], module_name.strip()]))
                    else:  # pattern: import Abc
                        modules.append(groups[0])
        return modules

    @staticmethod
    def get_calling_func(parent_fnode, child_fnode, child_class_or_func: str):
        calling_func = None
        if child_fnode in parent_fnode.children_node_set:
            pattern = re.compile("def (\w*?)\(.*?\):.*?{}".format(child_class_or_func), re.DOTALL)
            matches = re.findall(pattern, parent_fnode.content_str)
            if matches:
                calling_func = matches[0]
        return calling_func

    @staticmethod
    def get_calling_class(parent_fnode, child_fnode, child_class_or_func: str):
        calling_class = None
        if child_fnode in parent_fnode.children_node_set:
            pattern = re.compile("class (\w*?):.*?{}".format(child_class_or_func), re.DOTALL)
            matches = re.findall(pattern, parent_fnode.content_str)
            if matches:
                calling_class = matches[0]
        return calling_class


class ParserSelector:
    lang_parser_dict = {
        "python":  PythonParser(),
        "python3": PythonParser()
    }

    suffix_parser_dict = {
        ".py": PythonParser(),
        "py":  PythonParser()
    }

    @classmethod
    def get_parser(cls, lang_or_suffix):
        if lang_or_suffix in cls.lang_parser_dict:
            return cls.lang_parser_dict[lang_or_suffix]
        if lang_or_suffix in cls.suffix_parser_dict:
            return cls.suffix_parser_dict[lang_or_suffix]
