import os


class GitIgnoreHelper:
    def __init__(self, root_path):
        """
        search .gitignore file in the given root_path
        :param root_path:
        """
        self.root_path = root_path
        self.ignore_pattern_list = self.setup_ignore_pattern(self.root_path)

    def setup_ignore_pattern(self, root_path):
        possible_ignore_file = os.path.join(root_path, '.gitignore')
        if not os.path.isfile(possible_ignore_file):
            return []
        with open(possible_ignore_file, 'r') as fp:
            patterns = fp.readlines()
        filtered_patterns = []
        for pattern in patterns:
            if not pattern.startswith('#'):
                filtered_patterns.append(pattern)
        return filtered_patterns

    def is_ignored(self, file_path):
        file_path = PathUtils.strip_root_path(file_path, self.root_path)
        for pattern in self.ignore_pattern_list:
            if self.is_pattern_matched(pattern, file_path):
                return True
        return False

    @staticmethod
    def is_pattern_matched(pattern, file_path):
        return PathUtils.is_matching(pattern, file_path, total_match=not pattern.endswith('/'))


class PathUtils:
    @staticmethod
    def is_matching(pattern, string, total_match=False):
        """
        check if string is matching the pattern which may contains '*' as any chars
        :param pattern: str, relevant shorter than string
        :param string: str, relevant longer than pattern
        :param total_match: bool, whether it needs to match to whole string
        :return: boolean
        """
        if len(pattern) == 0:
            return len(string) == 0 if total_match else True
        if len(string) == 0:
            return len(pattern) == 1 and pattern[0] == '*'
        if pattern[0] != '*':
            if pattern[0] != string[0]:
                return False
            else:
                return PathUtils.is_matching(pattern[1:], string[1:], total_match)
        else:
            if len(pattern) == 1:
                return True
            # assume there's only 1 * char in pattern
            str_i = 0
            while str_i < len(string) and string[str_i] != pattern[1]:
                str_i += 1
            if str_i == len(string):
                return False
            return PathUtils.is_matching(pattern[1:], string[str_i:], total_match)

    @staticmethod
    def strip_root_path(path, root_path):
        """
        remove root_path from path and return the rest
        :param path: origin path
        :param root_path: root_path
        :return: path that comes from origin path but strip the root_path
        """
        start_index = path.find(root_path)
        if start_index < 0:
            return path
        return path[start_index + len(root_path):]

    @staticmethod
    def is_having_ignore_keywords(file_path, ignore_keywords):
        """
        check if file_path contains any ignore keywords
        :param file_path: str
        :param ignore_keywords: list of keywords strings
        :return: boolean
        """
        return any(ignore_kw in file_path for ignore_kw in ignore_keywords)

    @staticmethod
    def normalize_to_abs(path):
        """
        change path to absolute path
        :param path: str
        :return: str
        """
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            return os.path.abspath(path)
        return path
