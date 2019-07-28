import unittest

from source_hunter.utils.path_utils import PathUtils


class PathUtilTest(unittest.TestCase):
    def test_is_matching(self):
        pattern = 'models/'
        true_string = 'models/residence'
        false_string1 = '.model/residence'
        false_string2 = '/models'

        self.assertTrue(PathUtils.is_matching(pattern, true_string))
        self.assertFalse(PathUtils.is_matching(pattern, true_string, total_match=True))
        self.assertFalse(PathUtils.is_matching(pattern, false_string1))
        self.assertFalse(PathUtils.is_matching(pattern, false_string2))

        pattern = '*_models/'
        true_string = 'residence_models/'
        false_string = 'residence_models'
        self.assertTrue(PathUtils.is_matching(pattern, true_string))
        self.assertFalse(PathUtils.is_matching(pattern, false_string))

        pattern = '*.py'
        true_string1 = 'residence.py'
        true_string2 = 'models/residence.py'
        true_string3 = 'residence/*/models/residence.py'
        false_string1 = 'residence.sh'
        false_string2 = '***.**.p*'

        self.assertTrue(PathUtils.is_matching(pattern, true_string1))
        self.assertTrue(PathUtils.is_matching(pattern, true_string2))
        self.assertTrue(PathUtils.is_matching(pattern, true_string3))
        self.assertFalse(PathUtils.is_matching(pattern, false_string1))
        self.assertFalse(PathUtils.is_matching(pattern, false_string2))

    def test_is_having_ignore_keywords(self):
        ignore_keywords = ['migration', 'test']
        file_path1 = '/scripts/migration_2019_11_28_disable_488_combination'
        file_path2 = '/xkool_site/components/calculator/architecture_calculator_test.py'

        self.assertTrue(PathUtils.is_having_ignore_keywords(file_path1, ignore_keywords))
        self.assertTrue(PathUtils.is_having_ignore_keywords(file_path2, ignore_keywords))
