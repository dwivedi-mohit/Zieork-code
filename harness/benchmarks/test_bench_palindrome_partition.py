
import unittest
from harness.benchmarks.palindrome import partition_palindromes

class TestPalindrome(unittest.TestCase):
    def test_partition_aab(self):
        res = partition_palindromes("aab")
        expected = [["a", "a", "b"], ["aa", "b"]]
        self.assertEqual(sorted([sorted(x) for x in res]), sorted([sorted(x) for x in expected]))
    def test_single_char(self):
        self.assertEqual(partition_palindromes("a"), [["a"]])

if __name__ == '__main__':
    unittest.main()
