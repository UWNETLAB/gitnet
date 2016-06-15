import unittest
import os
import warnings
import subprocess as sub
import gitnet
import sys
from unittest.mock import patch
from io import StringIO
import pandas as pd
from pandas.util.testing import assert_frame_equal

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
    def setUp(self):
        data = {"Alice": {"email": 'alice@gmail.com',
                          "type": 'author',
                          "loc": 'Waterloo'},
                "Bobby": {"email": 'bobby@gmail.com',
                          "type": 'author',
                          "loc": 'Kitchener'}}

        self.log = gitnet.Log(data)
        self.attr = self.log.attributes()

    def test_basic(self):
        """Is a list returned from the method?"""
        self.assertIsInstance(self.attr, list)

    def test_values(self):
        """Are the correct values returned by the method"""
        attr_list = ['email', 'loc', 'type'] # Sorted list
        self.assertListEqual(self.attr, attr_list)


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
        data = {"Alice": {"name": "Ms Alice Smith",
                          "email": 'alice@gmail.com',
                          "type": 'author',
                          "loc": 'Waterloo',
                          "books": ['BookA', 'BookB'],
                          "date": 'Sat May 7 15:41:25 2016 -0400'},
                "Bobby": {"name": "Mr Bobby",
                          "email": 'bobby_smith@gmail.ca',
                          "type": 'author',
                          "loc": 'Kitchener',
                          "books": ['BookC', 'BookM'],
                          "date": 'Thu May 5 15:41:25 2016 -0400'}}
        self.log = gitnet.Log(data)

    def test_equals(self):
        """Does the equals function perform correctly?"""
        # Filter out Alice
        res = self.log.filter("email", "equals", "bobby_smith@gmail.ca")
        self.assertIsInstance(res, gitnet.Log)
        self.assertNotIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out neither
        res = self.log.filter("type", "equals", "author")
        self.assertIsInstance(res, gitnet.Log)
        self.assertIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out both
        res = self.log.filter("email", "equals", "charles@gmail.uk")
        self.assertIsInstance(res, gitnet.Log)
        self.assertNotIn('Alice', res)
        self.assertNotIn('Bobby', res)

    def test_has(self):
        """Does the has function perform correctly?"""
        # Filter out Bobby
        res = self.log.filter("email", "has", "@gmail.com")
        self.assertIn('Alice', res)
        self.assertNotIn('Bobby', res)

        # Filter out neither
        res = self.log.filter("email", "has", "@gmail.c[oa]m?")
        self.assertIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out both
        res = self.log.filter("books", "has", "BookZ")
        self.assertNotIn('Alice', res)
        self.assertNotIn('Bobby', res)

    def test_since(self):
        # Filter out Bobby
        res = self.log.filter("date", "since", "Fri May 6 15:41:25 2016 -0400")
        self.assertIn('Alice', res)
        self.assertNotIn('Bobby', res)

        # Filter out neither
        res = self.log.filter("date", "since", "Wed May 5 15:41:25 2016 -0400")
        self.assertIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out both
        res = self.log.filter("date", "since", "Sun May 8 15:41:25 2016 -0400")
        self.assertNotIn('Alice', res)
        self.assertNotIn('Bobby', res)

    def test_before(self):
        # Filter out Bobby
        res = self.log.filter("date", "before", "Fri May 6 15:41:25 2016 -0400")
        self.assertNotIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out both
        res = self.log.filter("date", "before", "Mon May 2 15:41:25 2016 -0400")
        self.assertNotIn('Alice', res)
        self.assertNotIn('Bobby', res)

        # Filter out neither
        res = self.log.filter("date", "before", "Sun May 8 15:41:25 2016 -0400")
        self.assertIn('Alice', res)
        self.assertIn('Bobby', res)

    def test_any(self):
        """Does tag = any work properly?"""
        # Filter out Alice
        res = self.log.filter("any", "has", 'smith')
        self.assertNotIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out neither
        res = self.log.filter("any", "has", "(S|s)mith")
        self.assertIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out both
        res = self.log.filter("any", "has", "x")
        self.assertNotIn('Alice', res)
        self.assertNotIn('Bobby', res)

    def test_any_helper(self):
        def myin(val, chk):
            if chk in val:
                return True
            else:
                return False

        # Filter out Alice
        res = self.log.filter(tag="any", fun="has", match='Mr', helper=myin, summary="Checks if Titled")
        self.assertNotIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out neither
        res = self.log.filter(tag="any", fun="has", match="M", helper=myin, summary="Checks if Titled")
        self.assertIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out both
        res = self.log.filter(tag="any", fun="has", match="PhD", helper=myin, summary="Checks if Titled")
        self.assertNotIn('Alice', res)
        self.assertNotIn('Bobby', res)

        # Filter by list items
        res = self.log.filter("any", "has", "Book", helper=myin, summary="Check if Book is there")
        self.assertIn('Alice', res)
        self.assertIn('Bobby', res)

    def test_warnings(self):
        # Warning occurs when dates are compared using <,<=,>,>= functions
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            self.log.filter("date", "<", 'Fri May 6 15:41:25 2016 -0400')
            # Check Warning occurred
            self.assertEqual(len(w), 1)
            self.assertIn("Dates have been compared alphabetically with <, "
                          "use Datetime comparisons to compare dates by time.", str(w[-1].message))


class TsvTests(unittest.TestCase):
    def setUp(self):
        # Creating a log object
        data = {"Alice": {"email": 'alice@gmail.com',
                          "type": 'author',
                          "loc": 'Waterloo',
                          "books": ['BookA', 'BookB'],
                          "stars": [4, 5]},
                "Bobby": {"email": 'bobby@gmail.com',
                          "type": 'author',
                          "loc": 'Kitchener',
                          "books": ['BookC', 'BookD'],
                          "stars": [4, 4]}}
        self.log = gitnet.Log(data)

        # Setting up the directory for the tsv
        self.made_tsv = False
        try:
            self.tsv_str = self.log.tsv(fname='temp.tsv')
            self.path = os.getcwd() + '/temp.tsv'
        finally:
            self.made_tsv = True
            print(self.made_tsv)

    def test_basic_fn(self):
        """Is a file produced and a summary string given?"""
        # Check that the method doesn't return a value
        self.assertIsInstance(self.tsv_str, str)
        # Check that a file exists where expected
        self.assertTrue(os.path.exists(self.path))
        # Check a summary string is produced
        self.assertEqual("Data written to temp.tsv", self.tsv_str)

    def test_basic_nofn(self):
        """Is no file produced but a string given? """
        # Removing the setup file
        self.made_tsv = False
        sub.call(['rm', 'temp.tsv'])
        # Checking no file is created
        self.assertFalse(os.path.exists(self.path))
        # Checking a correct string is returned
        tsv_str = self.log.tsv()
        self.assertIsInstance(tsv_str, str)
        self.assertIn('\t', tsv_str)

    def test_empty_cols(self):
        tsv_str = self.log.tsv(empty_cols=True, fname='temp.tsv')
        # Checking file is created
        self.assertTrue(os.path.exists(self.path))
        # Check a summary string is produced
        self.assertEqual("Data written to temp.tsv", tsv_str)

    def test_list_attr(self):
        pass

    def test_warnings(self):
        # Warning occurs non string values are forced to strings
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            self.log.tsv()
            # Check Warning occurred
            self.assertIn("Non-string input forced to string", str(w[-1].message))

    def tearDown(self):
        if self.made_tsv:
            sub.call(['rm', 'temp.tsv'])


class DataFrameTests(unittest.TestCase):
    def setUp(self):
        # Creating a log object
        data = {"Alice": {"email": 'alice@gmail.com',
                          "type": 'author',
                          "loc": 'Waterloo',
                          "books": ['BookA', 'BookB'],
                          "stars": [4, 5]},
                "Bobby": {"email": 'bobby@gmail.com',
                          "type": 'author',
                          "loc": 'Kitchener',
                          "books": ['BookC', 'BookD'],
                          "stars": [4, 4]}}
        self.log = gitnet.Log(data)

        self.df = self.log.df()

    def test_basic(self):
        """Check that a dataframe is produced"""
        self.assertIsInstance(self.df, pd.DataFrame)

    def test_values(self):
        columns = ['books', 'email', 'loc', 'stars', 'type']
        index = ['Alice', 'Bobby']
        data = [[['BookA', 'BookB'], 'alice@gmail.com', 'Waterloo', [4, 5], 'author'],
                [['BookC', 'BookD'], 'bobby@gmail.com', 'Kitchener', [4, 4], 'author']]

        expected_df = pd.DataFrame(columns=columns, index=index, data=data)
        # Checking the created dataframe matches the expected dataframe
        assert_frame_equal(expected_df, self.df)


class VectorTests(unittest.TestCase):
    def setUp(self):
        # Creating a log object
        data = {"Alice": {"email": 'alice@gmail.com',
                          "type": 'author',
                          "loc": 'Waterloo',
                          "books": ['BookA', 'BookB'],
                          "stars": [4, 5]},
                "Bobby": {"email": 'bobby@gmail.com',
                          "type": 'author',
                          "loc": 'Kitchener',
                          "books": ['BookC', 'BookD'],
                          "stars": [4, 4]}}
        self.log = gitnet.Log(data)

    def test_basic(self):
        """Is a list returned?"""
        log = self.log
        vect = log.vector("email")
        # Is vect a list that contains at least one correct element?
        self.assertIsInstance(vect, list)
        self.assertIn("alice@gmail.com", vect)

    def test_values(self):
        """Are the results of .vector correct?"""
        log = self.log
        vect_e = log.vector("email")
        self.assertSetEqual(set(vect_e), {'alice@gmail.com', 'bobby@gmail.com'})
        vect_t = log.vector("type")
        self.assertSetEqual(set(vect_t), {'author'})
        vect_l = log.vector("loc")
        self.assertSetEqual(set(vect_l), {'Waterloo', 'Kitchener'})
        vect_b = log.vector("books")
        self.assertSetEqual(set(vect_b), {'BookC', 'BookD', 'BookA', 'BookB'})
        vect_s = log.vector("stars")
        self.assertSetEqual(set(vect_s), {4, 5})

    def test_notag(self):
        """Does the method act as expected when a tag doesn't exist"""
        log = self.log
        vect_notag = log.vector("phone_num")
        self.assertListEqual(vect_notag, [])


class ReplaceValTests(unittest.TestCase):
    """Tests for the replace value function in the Log class."""

    def setUp(self):
        # Set up small network
        sub.call(["cp","-R","small_network_repo.git",".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)
        pass

    def test_author_replace(self):
        self.my_log = self.my_log.replace_val("author", "Billy G", "Willy")
        self.assertEqual(self.my_log.collection["6cd4bbf"]["author"], "Willy")

    def test_email_replace(self):
        self.my_log = self.my_log.replace_val("email", "bill@gmail.com", "willy@gmail.com")
        self.assertEqual(self.my_log.collection["6cd4bbf"]["email"], "willy@gmail.com")

    def test_fedits_replace(self):
        # Note that replacing fedits is not good practice unless you know for certain that it should be changed to reflect reality.
        # Also, numeric data is represented in the log collection by an integer.
        self.my_log = self.my_log.replace_val("fedits", 2, 7)
        self.assertEqual(self.my_log.collection["7965e62"]["fedits"], 7)

    def test_bad_tag(self):
        # Warning occurs when vector edge and node attributes are provided
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            replacement = self.my_log.replace_val("gitmaster", "Billy G", "William")
            # Check Warning occurred
            self.assertEqual(len(w), 1)
            self.assertIn("The tag requested does not appear in this collection.", str(w[-1].message))

    def test_no_value(self):
        # Warning occurs when vector edge and node attributes are provided
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            replacement = self.my_log.replace_val("author", "Jan", "Janice")
            # Check Warning occurred
            self.assertEqual(len(w), 1)
            self.assertIn("The value requested does not appear in any records in this collection.", str(w[-1].message))

    def tearDown(self):
        sub.call(["rm","-rf",".git"])

#
#
# class GenEdgesTests(unittest.TestCase):  # I think this may be covered in test_netgen.py
#     def setup(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#
# class GenNodesTests(unittest.TestCase):  # I think this may be covered in test_netgen.py
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#
# class GenNetworkTests(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#
# class WriteEdgesTests(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         pass
#
#
# class WriteNodesTests(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def tearDown(self):
#         pass


if __name__ == '__main__':
    unittest.main(buffer=True)
