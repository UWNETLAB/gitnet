import unittest
import os
import warnings
import subprocess as sub
import gitnet
import sys
from unittest.mock import patch
from io import StringIO


"""This file houses the tests for log.py. However, network generation methods such as generate_edges() are tested
in test_netgen.py."""


class GetTagsTests(unittest.TestCase):
    def setUp(self):
        data = {"Alice": {"email": 'alice@gmail.com',
                          "type": 'author',
                          "loc": 'Waterloo'},
                "Bobby": {"email": 'bobby@gmail.com',
                          "type": 'author',
                          "loc": 'Kitchener'}}
        self.log = gitnet.Log(data)

    def test_basic(self):
        """Does log.get_tags return an empty list as expected?"""
        self.assertIsInstance(self.log, gitnet.Log)
        self.assertListEqual(self.log.get_tags(), [])


class AttributesTests(unittest.TestCase):
    def setup(self):
        pass


class DescribeTests(unittest.TestCase):
    def setUp(self):
        data = {"Alice": {"email": 'alice@gmail.com',
                          "type": 'author',
                          "loc": 'Waterloo'},
                "Bobby": {"email": 'bobby@gmail.com',
                          "type": 'author',
                          "loc": 'Kitchener'}}
        self.log = gitnet.Log(data)

    def test_basic(self):
        self.log.describe()
        self.assertIsNotNone(self.log.describe())
        self.assertIsInstance(self.log.describe(), str)

    def test_print(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.log.describe()
            self.assertIn("Log containing 2 records from None created at", fake_out.getvalue())
            self.assertNotIn("Filter:", fake_out.getvalue())

    def test_filter_print(self):
        self.log.filters = ["{} {} {} | Negate: {} | Helper: {}".format('age', '>', 10, False, None)]

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.log.describe()
            self.assertRegex(fake_out.getvalue(),
                             "Log containing 2 records from None created at ....-..-.. ..:..:..\.......\.\n"
                             "None\n"
                             "Filters:\tage > 10 | Negate: False | Helper: None")


class BrowseTests(unittest.TestCase):
    def setUp(self):
        data = {"Alice": {"email": 'alice@gmail.com',
                          "type": 'author',
                          "loc": 'Waterloo',
                          "books": ['BookA', 'BookB']},
                "Bobby": {"email": 'bobby@gmail.com',
                          "type": 'author',
                          "loc": 'Kitchener',
                          "books": ['BookC', 'BookD']}}
        self.log = gitnet.Log(data)

    def test_quit(self):
        """Is the output as expected upon the input of q?"""
        with patch("sys.stdin", StringIO("q")), patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.log.browse()
            self.assertTrue("-- Alice --" in fake_out.getvalue() and "-- Bobby --" not in fake_out.getvalue() or
                            "-- Bobby --" in fake_out.getvalue() and "-- Alice --" not in fake_out.getvalue())

    def test_attr(self):
        with patch("sys.stdin", StringIO("q")), patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.log.browse()
            self.assertTrue("Waterloo" in fake_out.getvalue() and "Kitchener" not in fake_out.getvalue() or
                            "Kitchener" in fake_out.getvalue() and "Waterloo" not in fake_out.getvalue())
            self.assertIn("author", fake_out.getvalue())
            self.assertTrue("BookA\nBookB" in fake_out.getvalue() and "BookC\nBookD" not in fake_out.getvalue() or
                            "BookC\nBookD" in fake_out.getvalue() and "BookA\nBookB" not in fake_out.getvalue())


class FilterTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class TsvTests(unittest.TestCase):
    def setup(self):
        pass

    def tearDown(self):
        pass


class DataFrameTests(unittest.TestCase):
    def setup(self):
        pass

    def tearDown(self):
        pass


class VectorTests(unittest.TestCase):
    def setup(self):
        pass

    def tearDown(self):
        pass


class ReplaceValTests(unittest.TestCase):
    def setup(self):
        pass

    def tearDown(self):
        pass


class GenEdgesTests(unittest.TestCase):  # I think this may be covered in test_netgen.py
    def setup(self):
        pass

    def tearDown(self):
        pass


class GenNodesTests(unittest.TestCase):  # I think this may be covered in test_netgen.py
    def setUp(self):
        pass

    def tearDown(self):
        pass


class GenNetworkTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class WriteEdgesTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class WriteNodesTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main(buffer=True)