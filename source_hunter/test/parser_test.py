from unittest import TestCase

from source_hunter.parser import PythonParser

content1 = """
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
    def fnode_by_import(self, import_content, cur_dir):
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
"""

content2 = """
import re
from typing import List
from abc import ABC, abstractmethod
from source_hunter.utils.log_utils import logger
from collections import OrderedDict
"""

content3 = """
import json
import numpy
from shapely.geometry import Polygon
import shapely


def gen_poly():
    return Polygon([(0, 0), (1, 0), (0, 1)])

def shape(poly):
    return shapely.geometry.shape(poly)
"""


class PythonParserTest(TestCase):
    def test_parse_structure(self):
        code_structure = PythonParser.parse_structure(content1)
        first_level = ['from source_hunter.utils.path_utils import PathUtils',
                       'class BaseFinder(ABC):',
                       'class PythonFinder(BaseFinder):']
        self.assertListEqual(first_level, list(code_structure.keys()))
        self.assertEqual(2, len(code_structure['class BaseFinder(ABC):']))
        self.assertEqual(1, len(
            code_structure['class BaseFinder(ABC):']['    def fnode_by_import(self, import_content, cur_dir):']))

    def test_parse_children_modules(self):
        modules = PythonParser.parse_children_modules(content2)
        self.assertEqual(6, len(modules))
        expected_modules = {
            're',
            'typing.List',
            'abc.ABC',
            'abc.abstractmethod',
            'source_hunter.utils.log_utils.logger',
            'collections.OrderedDict'
        }
        self.assertSetEqual(expected_modules, set(modules))

    def test_get_caller(self):
        calling_item = set(PythonParser.get_caller(content1, 'PathUtils'))
        self.assertSetEqual(set(['PythonFinder', 'fnode_by_import']), calling_item)

    def test_get_deps(self):
        deps_item = set(PythonParser.get_deps(content1, 'PythonFinder'))
        self.assertSetEqual({'source_hunter.utils.path_utils.PathUtils.strip_root_path'}, deps_item)

        deps_item = set(PythonParser.get_deps(content3, 'shape'))
        self.assertSetEqual({'shapely.geometry.shape'}, deps_item)
