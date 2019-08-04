import os
from queue import Queue
from source_hunter.result import Result
from source_hunter.utils.log_utils import logger


class Query:
    def __init__(self, deps_tree):
        """
        :param deps_tree: deps_tree obj
        """
        self.deps_tree = deps_tree

    def _find_caller_query_helper(self, module_path, class_or_func, seen, result):
        callee_fnode = self.deps_tree.path_fnode_dict.get(module_path, None)
        if callee_fnode and callee_fnode not in seen:
            seen.add(callee_fnode)
            for caller_fnode in callee_fnode.parents:
                calling_items = caller_fnode.get_caller(class_or_func)
                if calling_items:
                    result.add_calling_relation(callee_fnode, caller_fnode)
                for calling_item in calling_items:
                    self._find_caller_query_helper(caller_fnode.file_path, calling_item, seen, result)
        return result

    def find_caller(self, module_path, class_or_func):
        result = Result(self.deps_tree.root_path)
        return self._find_caller(module_path, class_or_func, result)

    def _find_caller(self, module_path, class_or_func, result=None):
        if not result:
            result = Result(self.deps_tree.root_path)
        self._find_caller_query_helper(module_path, class_or_func, set(), result)
        logger.info('result contains {} relationship'.format(len(result.relationship)))
        return result

    def find_deps(self, module_path, class_or_func):
        result = Result(self.deps_tree.root_path)
        return self._find_deps(module_path, class_or_func, result)

    def _find_deps(self, module_path, class_or_func, result=None):
        if not result:
            result = Result(self.deps_tree.root_path)
        start_fnode = self.deps_tree.path_fnode_dict.get(module_path, None)
        if start_fnode:
            stack = []
            for dep in start_fnode.get_deps(class_or_func):
                stack.append((dep, start_fnode))
            while stack:
                dep, caller_fnode = stack.pop()
                dep_fnode = self.deps_tree.finder.fnode_by_import(dep, caller_fnode.dir_path)
                if dep_fnode:
                    result.add_calling_relation(dep_fnode, caller_fnode)
                    module_name = os.path.basename(dep_fnode.file_path).split('.')[0]
                    dep_name_idx = dep.find(module_name)
                    if dep_name_idx > 0:
                        dep_class_or_func = dep[dep_name_idx + len(module_name):]
                        if dep_class_or_func.startswith('.'):
                            dep_class_or_func = dep_class_or_func[1:]
                        for dep in dep_fnode.get_deps(dep_class_or_func):
                            stack.append((dep, dep_fnode))
        return result

    def find_caller_and_deps(self, module_path, class_or_func):
        result = Result(self.deps_tree.root_path)
        self._find_deps(module_path, class_or_func, result)
        self._find_caller(module_path, class_or_func, result)
        return result
