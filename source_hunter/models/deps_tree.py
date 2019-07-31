import os

from source_hunter.constant import lang_suffix_mapping
from source_hunter.models.fnode import FNode
from source_hunter.finder import FinderSelector
from source_hunter.utils.log_utils import logger
from source_hunter.utils.path_utils import GitIgnoreHelper, PathUtils


class DepsTree:
    def __init__(self, root_path, lang='python', ignore_keywords=None, gitignore=False):
        self.ignore_keywords = [] if ignore_keywords is None else ignore_keywords
        self.root_path = root_path
        self.suffix = lang_suffix_mapping[lang]
        self.path_fnode_dict = self.setup_path_fnode_dict(self.root_path, gitignore)
        self.finder = FinderSelector.get_finder(lang)(self.root_path, self.path_fnode_dict)
        self.setup_tree(self.path_fnode_dict, self.finder)

    def setup_path_fnode_dict(self, root_path, gitignore=True):
        ignore_helper = GitIgnoreHelper(root_path)
        result = {}
        for root, _, fnames in os.walk(root_path):
            for fname in fnames:
                if fname.endswith(self.suffix):
                    path = os.path.join(root, fname)
                    if (gitignore and ignore_helper.is_ignored(path)
                            or PathUtils.is_having_ignore_keywords(path, self.ignore_keywords)):
                        continue
                    result[path] = FNode(path)
        logger.info('scan {}, found {} fnodes'.format(self.root_path, len(result)))
        return result

    def setup_tree(self, path_fnode_dict, finder):
        for fnode in path_fnode_dict.values():
            for child_module in fnode.children_modules:
                child_fnode = finder.fnode_by_import(child_module, fnode.dir_path)
                if child_fnode:
                    fnode.add_child(child_fnode)
                    child_fnode.add_parent(fnode)
                    logger.verbose_info('setup_fnode_tree: {} -> {}'.format(fnode.file_path, child_fnode.file_path))
