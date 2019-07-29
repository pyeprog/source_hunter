from collections import defaultdict

from source_hunter.render import Renderer


class Result:
    def __init__(self, root_path):
        self.relationship = []
        self.root_path = root_path

    def add(self, parent_fnode, child_fnode):
        self.relationship.append((parent_fnode, child_fnode))

    def __repr__(self):
        """
        show the relationship in text format
        :return: str
        """
        children = set(map(lambda pair: pair[1], self.relationship))
        parent = set(map(lambda pair: pair[0], self.relationship))
        root = next(filter(lambda p: p not in children, parent))
        relation = defaultdict(list)
        for parent, child in self.relationship:
            relation[parent].append(child)

        result = []
        self._repr_helper(root, relation, result, has_next_sibling=False, has_connector_per_level=[])
        return '\n'.join(result)

    @staticmethod
    def _remove_path_duplicate(file_path, root_path):
        return file_path[len(root_path):]

    def _repr_helper(self, cur_fnode, mapping, result, has_next_sibling, has_connector_per_level):
        """
        print one line of the relationship text
        :param cur_fnode: fnode, current processing fnode
        :param mapping: dict, {callee_fnode: caller_fnode}
        :param result: list, final container of each line of relationship text
        :param has_next_sibling: whether current fnode has same level siblings
        :param has_connector_per_level: list, whether each level indentation should show '|', its length is used
            as indentation
        :return: None
        """
        cur_repr = ''
        for i, has_connector in enumerate(has_connector_per_level):
            cur_repr += '|' if has_connector else ' '
            cur_repr += '\t'
        cur_repr += '└>' + self._remove_path_duplicate(cur_fnode.file_path, self.root_path)
        result.append(cur_repr)

        children = mapping.get(cur_fnode, [])
        if len(has_connector_per_level) > 0 and has_next_sibling:
            has_connector_per_level.append(True)
        else:
            has_connector_per_level.append(False)
        for i, child_fnode in enumerate(children):
            self._repr_helper(child_fnode,
                              mapping,
                              result,
                              has_next_sibling=(i != len(children) - 1),
                              has_connector_per_level=has_connector_per_level)
        has_connector_per_level.pop()

    def render(self, name, dir_path, engine, ues_fullname=False, keep_suffix=False, view=True, output_format='pdf'):
        renderer = Renderer(self, name=name, use_fullname=ues_fullname, keep_suffix=keep_suffix, engine=engine)
        renderer.render(dir_path, view=view, output_format=output_format)
