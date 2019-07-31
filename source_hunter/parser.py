import re
from typing import List
from abc import ABC, abstractmethod
from source_hunter.utils.log_utils import logger


class BaseParser(ABC):
    def __init__(self, lang="python"):
        self.lang = lang

    @abstractmethod
    def parse_children_modules(content_lines: List[str]):
        """
        :param content_lines: list of str, lines of code
        :return: list of str, those statement that is responsible for import child module
        """
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def get_calling_func_or_class(parent_fnode, child_fnode, child_class_or_func: str):
        """
        check whether there is a func or class of parent_fnode calling the target child_class_or_func of child_fnode
        :param child_fnode: fnode
        :param child_class_or_func: str, target class or function name
        :return: list of str, function or class names that calling the child_class_or_func
        """
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
    def get_calling_func_or_class(parent_fnode, child_fnode, child_class_or_func: str):
        if child_fnode in parent_fnode.children_node_set:
            func_pattern = re.compile("def (\w*?)\(.*?\):.*?{}".format(child_class_or_func), re.DOTALL)
            func_matches = re.findall(func_pattern, parent_fnode.content_str)
            logger.verbose_info(
                'matching def (\w*?)\(.*?\):.*?{} in {}: {}'.format(child_class_or_func, parent_fnode.file_path,
                                                                    func_matches))

            class_pattern = re.compile("class (\w*?):.*?{}".format(child_class_or_func), re.DOTALL)
            class_matches = re.findall(class_pattern, parent_fnode.content_str)
            logger.verbose_info(
                'matching class (\w*?):.*?{} in {}: {}'.format(child_class_or_func, parent_fnode.file_path,
                                                                 class_matches))

            matches = []
            matches.extend(ma for ma in class_matches if ma)
            matches.extend(ma for ma in func_matches if ma and ma != '__init__')
            if matches:
                logger.info(
                    're.matching {} in {}: {}'.format(child_class_or_func, parent_fnode.file_path, matches))
        return matches


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
