import unittest
from ece241_submission_static_analyzer.rules.require_file import _is_file_exist  # type: ignore


class TestRequiredRule(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
        _is_file_exist("non_existent_file.txt")


if __name__ == "__main__":
    unittest.main()
