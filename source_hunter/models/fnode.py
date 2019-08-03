import os
from typing import List
from uuid import uuid4

from source_hunter.parser import ParserSelector


class FNode:
    def __init__(self, file_path):
        self.id = uuid4()
        self.file_path = file_path
        self.dir_path = os.path.dirname(file_path)
        self.content_lines = self.load(self.file_path)
        self.content_str = "\n".join(self.content_lines)
        self._parser_class = ParserSelector.get_parser(self.file_path.split(".")[-1])
        self._parser = self._parser_class(self.content_str)
        self.parent_node_set = set()
        self.children_node_set = set()
        self.children_modules = self.parse_children_modules()

    @staticmethod
    def load(file_path):
        assert os.path.isfile(file_path)

        lines = []
        with open(file_path, "r") as fp:
            lines.extend(fp.readlines())
        return lines

    @property
    def parents(self):
        return list(self.parent_node_set)

    @property
    def children(self):
        return list(self.children_node_set)

    @property
    def parser(self):
        return self._parser

    def add_parent(self, node):
        self.parent_node_set.add(node)

    def add_child(self, node):
        self.children_node_set.add(node)

    def parse_children_modules(self):
        return self._parser.parse_children_modules()

    def get_calling_func_or_class(self, child_fnode, child_class_or_func: str):
        return child_fnode.parser.get_calling_func_or_class(self.content_str, child_class_or_func)
