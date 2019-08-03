import re
from typing import List
from abc import ABC, abstractmethod
from source_hunter.utils.log_utils import logger


class BaseParser(ABC):
    @abstractmethod
    def __init__(self, code_str: str):
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def parse_children_modules(self):
        """
        :return: list of str, those statement that is responsible for import child module
        """
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def get_calling_func_or_class(self, parent_code_str: str, child_class_or_func: str):
        """
        check whether there is a func or class of parent_fnode calling the target child_class_or_func of child_fnode
        :param parent_code_str: str, code string of parent fnode
        :param child_class_or_func: str, target class or function name
        :return: list of str, function or class names that calling the child_class_or_func
        """
        raise NotImplementedError("This method is not implemented")


class PythonParser(BaseParser):
    def __init__(self, code_str: str):
        self.code_str = code_str
        # TODO: add a code structure parsing method

    def parse_children_modules(self):
        modules = []
        # parse import in 'from example import ...' form
        import_pattern = re.compile('from ([\w.]+) import (\([\w, \n]+\)|[\w_, ]+\n)')
        matches = re.findall(import_pattern, self.code_str)
        for match in matches:
            pathes = match[0].strip().split('.')
            for mod in match[1].strip().replace('\n', '').split(','):
                if 'as' in mod:
                    mod = mod.split('as')[0]
                single_mod = pathes + [mod.strip()]
                modules.append('.'.join(single_mod))

        # parse import in 'import ...' form
        import_pattern = re.compile('[^ \w_]import ([\w_, ]+)')
        matches = re.findall(import_pattern, self.code_str)
        for match in matches:
            for single_mod in match.split(','):
                if 'as' in single_mod:
                    single_mod = single_mod.split('as')[0]
                modules.append(single_mod.strip())
        return modules

    def get_calling_func_or_class(self, parent_code_str: str, child_class_or_func: str):
        # TODO: rectify this function
        pass


class ParserSelector:
    lang_parser_dict = {
        "python":  PythonParser,
        "python3": PythonParser
    }

    suffix_parser_dict = {
        ".py": PythonParser,
        "py":  PythonParser
    }

    @classmethod
    def get_parser(cls, lang_or_suffix):
        if lang_or_suffix in cls.lang_parser_dict:
            return cls.lang_parser_dict[lang_or_suffix]
        if lang_or_suffix in cls.suffix_parser_dict:
            return cls.suffix_parser_dict[lang_or_suffix]
