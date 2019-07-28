import os
from abc import ABC, abstractmethod
from collections import defaultdict

from source_hunter.utils.path_utils import PathUtils


class BaseFinder(ABC):
    @abstractmethod
    def fnode_by_import(self, import_content, cur_dir):
        raise NotImplementedError("This method is not implemented")


class PythonFinder(BaseFinder):
    def __init__(self, root_path, path_fnode_dict):
        self.root_path = root_path
        self.path_tree = self.setup_path_tree(self.root_path)
        self.path_fnode_dict = path_fnode_dict

    def setup_path_tree(self, root_path):
        """
        make a dict that:
        {
            filename_A: {},
            filename_B: {},
            dirname_A: {
                    filename_C: {},
                    filename_D: {},
                  }
        }
        :param root_path: abs path of root
        :return: nested dict that representing the directory structure
        """
        path_tree = defaultdict(defaultdict)
        for full_name in os.listdir(root_path):
            name = full_name.split(".")[0]
            if os.path.isfile(os.path.join(root_path, full_name)):
                path_tree[name] = os.path.join(root_path, full_name)
            else:
                path_tree[name] = self.setup_path_tree(
                    os.path.join(root_path, full_name)
                )
        return path_tree

    def fnode_by_import(self, import_content, cur_dir):
        """
        :param import_content: import statement of a python module
        :param cur_dir: abs directory path of current file
        :return: abs file path of the import module
        """
        modules = []
        # relative import
        dot_count = 0
        for i in range(len(import_content)):
            if import_content[i] == '.':
                dot_count += 1
            else:
                break
        if dot_count > 0:
            for _ in range(dot_count - 1):
                if cur_dir.endswith('/'):
                    cur_dir = cur_dir[:-1]
                cur_dir = os.path.dirname(cur_dir)
            modules.extend([p for p in PathUtils.strip_root_path(cur_dir, self.root_path).strip().split('/') if p])

        modules.extend(import_content[dot_count:].split("."))
        cur_level = self.path_tree
        for module in modules:
            if isinstance(cur_level, str):
                break
            if module not in cur_level:
                break
            cur_level = cur_level[module]
        if not isinstance(cur_level, str):
            return None
        return self.path_fnode_dict.get(cur_level, None)


class FinderSelector:
    lang_finder_dict = {
        'python':  PythonFinder,
        'python3': PythonFinder,
    }
    suffix_finder_dict = {
        'py':  PythonFinder,
        '.py': PythonFinder,
    }

    @classmethod
    def get_finder(cls, lang_or_suffix):
        if lang_or_suffix in cls.lang_finder_dict:
            return cls.lang_finder_dict[lang_or_suffix]
        if lang_or_suffix in cls.suffix_finder_dict:
            return cls.suffix_finder_dict[lang_or_suffix]
