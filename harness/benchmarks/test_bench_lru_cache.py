
import unittest
from harness.benchmarks.lru_cache import LRUCache

class TestLRUCache(unittest.TestCase):
    def test_eviction(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        self.assertEqual(cache.get(1), 1)
        cache.put(3, 3) # evicts key 2
        self.assertEqual(cache.get(2), -1)
        cache.put(4, 4) # evicts key 1
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(3), 3)
        self.assertEqual(cache.get(4), 4)

if __name__ == '__main__':
    unittest.main()
