import os
from collections import defaultdict


class Finder:
    def __init__(self, root_path, path_fnode_dict):
        self.root_path = root_path
        self.path_tree = self.setup_path_tree(self.root_path)
        self.path_fnode_dict = path_fnode_dict

    def setup_path_tree(self, root_path):
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

    def fnode_by_import(self, import_content):
        modules = import_content.split(".")
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


if __name__ == "__main__":
    finder = Finder("/home/pd/projects/backend", {})
    print(finder.fnode_by_import("xkool_site.controller.residence_controller"))
