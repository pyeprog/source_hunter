import re
from typing import List
from abc import ABC, abstractmethod
from source_hunter.utils.log_utils import logger
from collections import OrderedDict


class BaseParser(ABC):
    @abstractmethod
    def parse_children_modules(code_str: str):
        """
        :param code_str: str, code string
        :return: list of str, those statement that is responsible for import child module
        """
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def get_caller(code_str: str, class_or_func: str):
        """
        check whether there is a func or class of parent_fnode calling the target child_class_or_func of child_fnode
        :param code_str: str, code string of parent fnode
        :param class_or_func: str, target class or function name
        :return: list of str, function or class names that calling the child_class_or_func
        """
        raise NotImplementedError("This method is not implemented")

    @abstractmethod
    def get_deps(code_str: str, class_or_func: str):
        """
        get dependent modules of the class or function specified by parameter
        :param class_or_func: str, class or function name
        :return: list of str
        """
        raise NotImplementedError("This method is not implemented")


class PythonParser(BaseParser):
    @staticmethod
    def parse_children_modules(code_str: str):
        modules = []
        # parse import in 'from example import ...' form
        import_pattern = re.compile('from ([\w.]+) import (\([\w, \n]+\)|[\w_, ]+\n)')
        matches = re.findall(import_pattern, code_str)
        for match in matches:
            pathes = match[0].strip().split('.')
            for mod in match[1].strip().replace('\n', '').split(','):
                if 'as' in mod:
                    mod = mod.split('as')[0]
                single_mod = pathes + [mod.strip()]
                modules.append('.'.join(single_mod))

        # parse import in 'import ...' form
        import_pattern = re.compile('[^ \w_]import ([\w_, ]+)')
        matches = re.findall(import_pattern, code_str)
        for match in matches:
            for single_mod in match.split(','):
                if 'as' in single_mod:
                    single_mod = single_mod.split('as')[0]
                modules.append(single_mod.strip())
        return modules

    @staticmethod
    def parse_structure(code_str: str):
        code_lines = code_str.split('\n')
        return PythonParser._parse_structure_helper(code_lines, 0)

    @staticmethod
    def _parse_structure_helper(code_lines: List[str], indent_level: int):
        same_indent_lines = []
        for i, code_line in enumerate(code_lines):
            if len(code_line) == 0:
                continue
            try:
                cur_indent_level = PythonParser.count_indent_level(code_line)
            except ValueError:
                continue
            if cur_indent_level == indent_level:
                same_indent_lines.append(i)

        code_structure = OrderedDict()
        for i, line_num in enumerate(same_indent_lines):
            if i < len(same_indent_lines) - 1:
                if line_num + 1 < same_indent_lines[i + 1]:
                    code_structure[code_lines[line_num]] = PythonParser._parse_structure_helper(
                        code_lines[line_num + 1: same_indent_lines[i + 1]], indent_level + 1)
                else:
                    code_structure[code_lines[line_num]] = {}
            else:
                if line_num + 1 < len(code_lines):
                    code_structure[code_lines[line_num]] = PythonParser._parse_structure_helper(
                        code_lines[line_num + 1:], indent_level + 1)
                else:
                    code_structure[code_lines[line_num]] = {}
        return code_structure

    @staticmethod
    def count_indent_level(line: str):
        i = 0
        while i < len(line) and line[i] == ' ':
            i += 1
        if not (i / 4).is_integer():
            raise ValueError('indented space is not multiple of 4')
        return i // 4

    @staticmethod
    def get_caller(code_str: str, class_or_func: str):
        code_structure = PythonParser.parse_structure(code_str)
        result = []
        PythonParser._get_caller_helper(code_structure, class_or_func, result)
        logger.verbose_info('searching {} found {}'.format(class_or_func, result))
        return result

    @staticmethod
    def _get_caller_helper(code_structure, class_or_func, result_container):
        result = {'func_call': [], 'class_call': [], 'variable_call': [], 'other_call': []}
        for statement, sub_structure in code_structure.items():
            result_of_sub = PythonParser._get_caller_helper(sub_structure, class_or_func, result_container)
            found = any(result_of_sub['func_call'] + result_of_sub['class_call'] + result_of_sub['variable_call'] +
                        result_of_sub['other_call'])
            if found:
                if 'def' in statement:
                    func_name = re.findall('def ([\w_]+)\([\w \t,_]*\):[\t ]*', statement)
                    result['func_call'].extend(func_name)
                    result_container.extend(func_name)
                elif 'class' in statement:
                    class_name = re.findall('class ([\w_]+).*:', statement)
                    result['class_call'].extend(class_name)
                    result_container.extend(class_name)
                else:
                    result['other_call'].extend(result_of_sub['other_call'])
            if class_or_func in statement:
                if '=' in statement and '==' not in statement and '<=' not in statement and '>=' not in statement:
                    statement_parts = statement.split('=')
                    result['variable_call'].extend(statement_parts[0].split(','))
                else:
                    result['other_call'].append(statement)
        return result

    @staticmethod
    def get_deps(code_str: str, class_or_func: str):
        modules = PythonParser.parse_children_modules(code_str)
        code_structure = PythonParser.parse_structure(code_str)
        deps_modules = []
        for statement, sub_structure in code_structure.items():
            if class_or_func in statement:
                for module in modules:
                    usages = PythonParser._get_deps_helper(sub_structure, module)
                    deps_modules.extend(usages)
        return list(set(deps_modules))

    @staticmethod
    def _get_deps_helper(code_structure, module):
        result = []
        mod = module.split('.')[-1]
        # module usage in 'module(...)' form
        direct_use_pattern = re.compile('{}\(.*?\)'.format(mod))
        # module usage in 'module.sub(...)' form
        use_sub_pattern = re.compile('{}([.\w_]*)\(.*?\)'.format(mod))

        for statement, sub_structure in code_structure.items():
            direct_usages = re.findall(direct_use_pattern, statement)
            if direct_usages:
                result.append(module)
            sub_mods = re.findall(use_sub_pattern, statement)
            for sub_mod in sub_mods:
                result.append(module + sub_mod)
            result.extend(PythonParser._get_deps_helper(sub_structure, module))
        return result


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
