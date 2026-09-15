
import unittest
from harness.benchmarks.levenshtein import levenshtein_distance

class TestLevenshtein(unittest.TestCase):
    def test_identical(self):
        self.assertEqual(levenshtein_distance("kitten", "kitten"), 0)
    def test_classic(self):
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)
    def test_empty(self):
        self.assertEqual(levenshtein_distance("", "test"), 4)
        self.assertEqual(levenshtein_distance("test", ""), 4)
    def test_substitution(self):
        self.assertEqual(levenshtein_distance("flaw", "lawn"), 2)

if __name__ == '__main__':
    unittest.main()
