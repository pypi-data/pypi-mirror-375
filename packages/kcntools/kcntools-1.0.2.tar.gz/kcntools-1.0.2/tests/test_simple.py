# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from kcntools.strutils import normalize


class TestSimple(unittest.TestCase):

    def test_add_one(self):
        self.assertEqual(normalize('这回事，'), '这回事,')


if __name__ == '__main__':
    unittest.main()
