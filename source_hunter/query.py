from source_hunter.result import Result
from source_hunter.utils.log_utils import logger


class Query:
    def __init__(self, deps_tree):
        """
        :param deps_tree: deps_tree obj
        """
        self.deps_tree = deps_tree

    def find_caller_query_helper(self, module_path, class_or_func, seen, result):
        start_fnode = self.deps_tree.path_fnode_dict.get(module_path, None)
        if start_fnode and start_fnode not in seen:
            seen.add(start_fnode)
            for parent_fnode in start_fnode.parents:
                calling_items = parent_fnode.get_calling_func_or_class(start_fnode, class_or_func)
                if calling_items:
                    result.add(start_fnode, parent_fnode)
                for calling_item in calling_items:
                    self.find_caller_query_helper(parent_fnode.file_path, calling_item, seen, result)
        return result

    def find_caller(self, module_path, class_or_func):
        result = Result(self.deps_tree.root_path)
        self.find_caller_query_helper(module_path, class_or_func, set(), result)
        logger.info('result contains {} relationship'.format(len(result.relationship)))
        return result
