from collections import defaultdict

from source_hunter.render import Renderer


class Result:
    def __init__(self, root_path):
        self.relationship = []
        self.root_path = root_path

    def add(self, parent_fnode, child_fnode):
        self.relationship.append((parent_fnode, child_fnode))

    def __repr__(self):
        children = set(map(lambda pair: pair[1], self.relationship))
        parent = set(map(lambda pair: pair[0], self.relationship))
        root = next(filter(lambda p: p not in children, parent))
        relation = defaultdict(list)
        for parent, child in self.relationship:
            relation[parent].append(child)

        result = []
        self._repr_helper(root, relation, result, level=0)
        return '\n'.join(result)

    @staticmethod
    def _remove_path_duplicate(file_path, root_path):
        return file_path[len(root_path):]

    def _repr_helper(self, start, mapping, result, level=0):
        cur_repr = '     |' * level + ('\b└' if level > 0 else '') + self._remove_path_duplicate(start.file_path,
                                                                                                 self.root_path)
        result.append(cur_repr)
        for next_ in mapping.get(start, []):
            self._repr_helper(next_, mapping, result, level=level + 1)

    def render(self, name, dir_path, engine, ues_fullname=False, keep_suffix=False, view=True):
        renderer = Renderer(self, name=name, use_fullname=ues_fullname, keep_suffix=keep_suffix, engine=engine)
        renderer.render(dir_path, view=view)
