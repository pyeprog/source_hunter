import os

from graphviz import Digraph


class Renderer:
    DEFAULT_STYLE = {
        "attr":      {"size": '6.6', 'ratio': 'compress'},
        "node_attr": {"color": "lightblue2", "style": "filled"},
    }

    def __init__(self, result, name="", style=None, use_fullname=False, keep_suffix=False, engine='dot'):
        style = self.DEFAULT_STYLE if not style else style
        self.name = name
        self.use_fullname = use_fullname
        self.keep_suffix = keep_suffix
        self.result = result
        self.dot = Digraph(name, engine=engine, graph_attr={'rankdir': 'LR'})
        self.dot.attr(size='8,5')
        self.dot.node_attr.update(color='lightblue2', style='filled')
        self.build_graph()

    def build_graph(self):
        relationship, parents, children = self.render_helper(self.result, use_fullname=self.use_fullname,
                                                             keep_suffix=self.keep_suffix)
        for parent in parents:
            self.dot.node(parent, parent)
        for child in children:
            self.dot.node(child, child)
        for parent, child in relationship:
            self.dot.edge(parent, child)

    @staticmethod
    def render_helper(result, use_fullname=False, keep_suffix=False):
        relationship = []
        parents = set()
        children = set()
        duplicate_filenames = set()
        if not use_fullname:
            filename_fnode_dict = {}
            for parent_fnode, child_fnode in result.relationship:
                parent_filename = os.path.basename(parent_fnode.file_path)
                child_filename = os.path.basename(child_fnode.file_path)
                if parent_filename not in filename_fnode_dict:
                    filename_fnode_dict[parent_filename] = parent_fnode
                elif filename_fnode_dict[parent_filename] != parent_fnode:
                    duplicate_filenames.add(parent_filename)
                if child_filename not in filename_fnode_dict:
                    filename_fnode_dict[child_filename] = child_fnode
                elif filename_fnode_dict[child_filename] != child_fnode:
                    duplicate_filenames.add(child_filename)

        for parent_fnode, child_fnode in result.relationship:
            parent_simple_path = result._remove_path_duplicate(
                parent_fnode.file_path, result.root_path
            )
            child_simple_path = result._remove_path_duplicate(
                child_fnode.file_path, result.root_path
            )
            if not use_fullname:
                if os.path.basename(parent_simple_path) not in duplicate_filenames:
                    parent_simple_path = os.path.basename(parent_fnode.file_path)
                if os.path.basename(child_simple_path) not in duplicate_filenames:
                    child_simple_path = os.path.basename(child_fnode.file_path)
            if not keep_suffix:
                parent_simple_path = parent_simple_path.split('.')[0]
                child_simple_path = child_simple_path.split('.')[0]

            # parents.add(parent_simple_path)
            # children.add(child_simple_path)
            relationship.append((parent_simple_path, child_simple_path))
        return relationship, parents, children

    def render(self, dir_path, view=True, output_format='pdf'):
        assert os.path.isdir(dir_path), "{} is not valid directory".format(dir_path)
        full_path = os.path.join(dir_path, self.name)
        self.dot.render(full_path, view=view, format=output_format)
