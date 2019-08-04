import os
from uuid import uuid4

from source_hunter.parser import ParserSelector


class FNode:
    def __init__(self, file_path):
        self.id = uuid4()
        self.file_path = file_path
        self.dir_path = os.path.dirname(file_path)
        self.content_lines = self.load(self.file_path)
        self.content_str = "\n".join(self.content_lines)
        self._parser = ParserSelector.get_parser(self.file_path.split(".")[-1])
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

    def add_parent(self, node):
        self.parent_node_set.add(node)

    def add_child(self, node):
        self.children_node_set.add(node)

    def parse_children_modules(self):
        return self._parser.parse_children_modules(self.content_str)

    def get_caller(self, class_or_func: str):
        return self._parser.get_caller(self.content_str, class_or_func)

    def get_deps(self, class_or_func: str):
        return self._parser.get_deps(self.content_str, class_or_func)
