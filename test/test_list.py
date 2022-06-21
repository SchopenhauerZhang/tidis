import time
import unittest

from rediswrap import RedisWrapper
from test_util import sec_ts_after_five_secs, msec_ts_after_five_secs


class ListTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = RedisWrapper().get_instance()

        cls.k1 = '__list1__'
        cls.k2 = '__list2__'

        cls.v1 = 'value1'
        cls.v2 = 'value2'

    def setUp(self):
        self.r.execute_command('del', self.k1)
        self.r.execute_command('del', self.k2)
        pass

    def test_lpop(self):
        for i in range(200):
            self.assertTrue(self.r.rpush(self.k1, str(i)))
        for i in range(200):
            self.assertEqual(self.r.lpop(self.k1), str(i))

    def test_lpush(self):
        for i in range(200):
            self.assertTrue(self.r.lpush(self.k1, str(i)))
        for i in range(200):
            self.assertEqual(self.r.rpop(self.k1), str(i))

    def test_rpop(self):
        for i in range(200):
            self.assertTrue(self.r.lpush(self.k1, str(i)))
        for i in range(200):
            self.assertEqual(self.r.rpop(self.k1), str(i))

    def test_rpush(self):
        for i in range(200):
            self.assertTrue(self.r.rpush(self.k1, str(i)))
        for i in range(200):
            self.assertEqual(self.r.lpop(self.k1), str(i))

    def test_llen(self):
        for i in range(200):
            self.assertTrue(self.r.rpush(self.k1, str(i)))
        self.assertEqual(self.r.llen(self.k1), 200)

    def test_lindex(self):
        for i in range(200):
            self.assertTrue(self.r.rpush(self.k1, str(i)))
        for i in range(200):
            self.assertEqual(self.r.lindex(self.k1, i), str(i))

    def test_lrange(self):
        for i in range(200):
            self.assertTrue(self.r.rpush(self.k1, str(i)))
        self.assertListEqual(self.r.lrange(self.k1, 10, 100), [str(i) for i in range(10, 101)])

        self.assertListEqual(self.r.lrange(self.k2, 0, 100), [])

    def test_lset(self):
        with self.assertRaises(Exception) as cm:
            self.r.lset(self.k1, 0, self.v1)
        err = cm.exception
        self.assertEqual(str(err), 'no such key')
        for i in range(200):
            self.assertTrue(self.r.rpush(self.k1, str(i)))
        self.assertTrue(self.r.lset(self.k1, 100, 'hello'))
        self.assertEqual(self.r.lindex(self.k1, 100), 'hello')

    def test_ltrim(self):
        for i in range(200):
            self.assertTrue(self.r.rpush(self.k1, str(i)))
        self.assertTrue(self.r.ltrim(self.k1, 0, 99))
        self.assertEqual(100, self.r.llen(self.k1))
        self.assertListEqual([str(i) for i in range(0, 100)], self.r.lrange(self.k1, 0, -1))

    def test_del(self):
        self.assertTrue(self.r.rpush(self.k1, self.v1))
        self.assertEqual(self.r.llen(self.k1), 1)
        self.assertEqual(self.r.execute_command('del', self.k1), 1)
        self.assertEqual(self.r.llen(self.k1), 0)

        # multi keys
        self.assertTrue(self.r.rpush(self.k2, self.v2))
        self.assertEqual(self.r.llen(self.k2), 1)
        self.assertEqual(self.r.execute_command("del", self.k1, self.k2), 1)
        self.assertEqual(self.r.llen(self.k2), 0)

    def test_persist(self):
        self.assertTrue(self.r.lpush(self.k1, self.v1))
        # expire in 5s
        self.assertTrue(self.r.execute_command('pexpire', self.k1, 5000))
        pttl = self.r.execute_command('pttl', self.k1)
        self.assertLessEqual(pttl, 5000)
        self.assertGreater(pttl, 0)
        self.assertEqual(self.r.llen(self.k1), 1)
        # persis the key
        self.assertEqual(self.r.persist(self.k1), 1)
        self.assertEqual(self.r.execute_command('pttl', self.k1), -1)

    def test_pexpire(self):
        self.assertTrue(self.r.lpush(self.k1, self.v1))
        # expire in 5s
        self.assertTrue(self.r.execute_command('pexpire', self.k1, 5000))
        pttl = self.r.execute_command('pttl', self.k1)
        self.assertLessEqual(pttl, 5000)
        self.assertGreater(pttl, 0)
        self.assertEqual(self.r.llen(self.k1), 1)
        time.sleep(6)
        self.assertEqual(self.r.llen(self.k1), 0)

    def test_pexpireat(self):
        self.assertTrue(self.r.lpush(self.k1, self.v1))
        # expire in 5s
        self.assertTrue(self.r.execute_command('pexpireat', self.k1, msec_ts_after_five_secs()))
        time.sleep(1)
        pttl = self.r.execute_command('pttl', self.k1)
        self.assertLess(pttl, 5000)
        self.assertGreater(pttl, 0)
        self.assertEqual(self.r.llen(self.k1), 1)
        time.sleep(6)
        self.assertEqual(self.r.llen(self.k1), 0)

    def test_expire(self):
        self.assertTrue(self.r.lpush(self.k1, self.v1))
        # expire in 5s
        self.assertTrue(self.r.execute_command('expire', self.k1, 5))
        ttl = self.r.execute_command('ttl', self.k1)
        self.assertLessEqual(ttl, 5)
        self.assertGreater(ttl, 0)
        self.assertEqual(self.r.llen(self.k1), 1)
        time.sleep(6)
        self.assertEqual(self.r.llen(self.k1), 0)

    def test_expireat(self):
        self.assertTrue(self.r.lpush(self.k1, self.v1))
        # expire in 5s
        self.assertTrue(self.r.execute_command('expireat', self.k1, sec_ts_after_five_secs()))
        ttl = self.r.execute_command('ttl', self.k1)
        self.assertLessEqual(ttl, 5)
        self.assertGreater(ttl, 0)
        self.assertEqual(self.r.llen(self.k1), 1)
        time.sleep(6)
        self.assertEqual(self.r.llen(self.k1), 0)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.r.execute_command('del', cls.k1)
        cls.r.execute_command('del', cls.k2)
        print('test data cleaned up')
