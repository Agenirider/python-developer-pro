import unittest

from scoring import get_store, is_redis_available, save_data_to_cache


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = get_store()
        self.is_redis_available = is_redis_available(self.store)
        self.sample = ['ABCDEF', '1234567890']

    def test_redis_available(self):
        self.assertTrue(self.is_redis_available)

    def test_redis_save_data_to_cache(self):
        key, sample = self.sample
        res = save_data_to_cache(key, sample)
        self.assertTrue(res)

    def test_get_data_from_cache(self):
        cashed_data = self.store.get(self.sample[0])
        if isinstance(cashed_data, bytes):
            self.assertEqual(cashed_data.decode('utf-8'), '1234567890')
        else:
            self.assertEqual(cashed_data.decode('utf-8'), '1234567890')


if __name__ == "__main__":
    unittest.main()
