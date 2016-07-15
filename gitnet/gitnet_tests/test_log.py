# *********************************************************************************************
# Copyright (C) 2016 Jillian Anderson, Joel Becker, Steve McColl and Dr. John McLevey
#
# This file is part of the gitnet package developed for Dr John McLevey's Networks Lab
# at the University of Waterloo. For more information, see http://networkslab.org/gitnet/.
#
# gitnet is free software: you can redistribute it and/or modify it under the terms of a
# GNU General Public License as published by the Free Software Foundation. gitnet is
# distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with gitnet.
# If not, see <http://www.gnu.org/licenses/>.
# *********************************************************************************************

import unittest
import os
import warnings
import subprocess as sub
import gitnet
from unittest.mock import patch
from io import StringIO
import pandas as pd
from pandas.util.testing import assert_frame_equal
import types


class MagicMethodTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

    def testinit(self):
        log = gitnet.Log()
        self.assertIsInstance(log, gitnet.Log)

    def test_str(self):
        string = str(self.my_log)
        self.assertRegex(string, "Log containing 4 records from local git created at ....-..-.. ..:..:..\.......\.")

    def test_len(self):
        self.assertEqual(len(self.my_log), 4)

    def tearDown(self):
        # Delete the temporary .git folder
        sub.call(["rm", "-rf", ".git"])


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
        attr_list = ['email', 'loc', 'type']  # Sorted list
        self.assertListEqual(self.attr, attr_list)

    def test_commit_log_values(self):
        """The same method pertains to a CommitLog, but the result may be different"""
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        path = os.getcwd()

        cl = gitnet.get_log(path)
        attr_list = cl.attributes()

        exp_attr_list = {"hash","author","email","date","mode","summary",
                         "fedits","inserts","message","files","changes"}

        self.assertSetEqual(set(attr_list), exp_attr_list)
        # Delete the temporary .git folder
        sub.call(["rm", "-rf", ".git"])


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


class AuthorEmailsTests(unittest.TestCase):
    """
    Tests for the author_email_list function.
    """
    def setUp(self):
        data = {"Bob": {"author": 'Bob',
                        "email": 'bob@gmail.com',
                        "type": 'author',
                        "loc": 'Waterloo',
                        "books": ['BookA', 'BookB']},
                "Bobby": {"author": 'Bobby',
                          "email": 'bobby@gmail.com',
                          "type": 'author',
                          "loc": 'Kitchener',
                          "books": ['BookC', 'BookD']},
                "Robert": {"author": 'Robert',
                           "email": 'robby@gmail.com',
                           "type": 'author',
                           "loc": 'Kitchener',
                           "books": ['BookC', 'BookD']}}
        self.log = gitnet.Log(data)

    def test_list_type(self):
        temp = self.log.author_email_list()
        self.assertIsInstance(temp, str)

    def test_output(self):
        temp = str(self.log.author_email_list())
        self.assertIn('robby@gmail.com   Robert', temp)
        self.assertIn('bob@gmail.com   Bob', temp)
        self.assertIn('bobby@gmail.com   Bobby', temp)

    def test_list_length(self):
        temp = len(self.log.author_email_list())
        self.assertEqual(temp, 263)


class DetectDuplicateEmailTests(unittest.TestCase):
    def setUp(self):
        data = {"Bob": {"author": 'Bob',
                        "email": 'bob@gmail.com',
                        "type": 'author'},
                "Bobby": {"author": 'Bobby',
                          "email": 'bob@gmail.com',
                          "type": 'author'},
                "Robert": {"author": 'Robert',
                           "email": 'bob@gmail.com',
                           "type": 'author'}}

        self.log = gitnet.Log(data)

    def test_basic(self):
        """Is a dictionary returned and something printed?"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            res = self.log.detect_dup_emails()
            self.assertIsInstance(res, dict)
            self.assertIsInstance(fake_out.getvalue(),str)
            self.assertNotEqual(fake_out.getvalue(), "")

    def test_dict(self):
        """Is a correct dictionary returned?"""
        dup_dict = self.log.detect_dup_emails()

        self.assertIn('bob@gmail.com', dup_dict)
        self.assertEqual(len(dup_dict), 1)

        self.assertEqual(len(dup_dict['bob@gmail.com']), 3)
        self.assertIn('Bob', dup_dict['bob@gmail.com'])
        self.assertIn('Bobby', dup_dict['bob@gmail.com'])
        self.assertIn('Robert', dup_dict['bob@gmail.com'])

    def test_print(self):
        """Are correct messages being printed?"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            for i in range(1000):
                self.log.detect_dup_emails()
                output = fake_out.getvalue()
                self.assertIn("Emails associated with multiple authors:\n", output)
                self.assertTrue("bob@gmail.com: ['Bob', 'Bobby', 'Robert']" in output or
                                "bob@gmail.com: ['Bob', 'Robert', 'Bobby']" in output or
                                "bob@gmail.com: ['Bobby', 'Bob', 'Robert']" in output or
                                "bob@gmail.com: ['Bobby', 'Robert', 'Bob']" in output or
                                "bob@gmail.com: ['Robert', 'Bob', 'Bobby']" in output or
                                "bob@gmail.com: ['Robert', 'Bobby', 'Bob']" in output)

                self.assertRegex(output, "Emails associated with multiple authors:"
                                         "\nbob@gmail.com: \[........................\]")

    def test_no_warnings(self):
        """Are warnings not printed at the right times?"""
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            self.log.detect_dup_emails()
            # Check no warning occurred
            self.assertEqual(len(w), 0)

    def test_warnings(self):
        """Are warnings printed at the right time?"""
        # Setting up a more complicated repository
        sub.call(["rm", "-rf", ".git"])
        sub.call(["cp", "-R", "repo_nx.git", ".git"])
        path = os.getcwd()
        nx_log = gitnet.get_log(path)

        # Note: Depending on the environment a warning may or may not be raised. For example, PyCharm uses UTF-8
        #       encoding and thus will not raised the unicode error.
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            nx_log.detect_dup_emails()
            # Check warning occurs
            self.assertTrue(len(w) == 0 or len(w) == 1)

    def tearDown(self):
        sub.call(["rm", "-rf", ".git"])


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
                          "books": ['BookA', 'BookB', 'BookX'],
                          "date": 'Sat May 7 15:41:25 2016 -0400'},
                "Bobby": {"name": "Mr Bobby",
                          "email": 'bobby_smith@gmail.ca',
                          "type": 'author',
                          "loc": 'Kitchener',
                          "books": ['BookC', 'BookM', 'BookX'],
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

    def test_lst_helper(self):
        def lst_helper(val, chk):
            if chk in val:
                return True
            else:
                return False

        # Filter out Alice
        res = self.log.filter('books', 'has', 'BookM', helper=lst_helper)
        self.assertNotIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out neither
        res = self.log.filter('books', 'has', 'BookX', helper=lst_helper)
        self.assertIn('Alice', res)
        self.assertIn('Bobby', res)

        # Filter out both
        res = self.log.filter('books', 'has', 'BookJ', helper=lst_helper)
        self.assertNotIn('Alice', res)
        self.assertNotIn('Bobby', res)

    def test_negate(self):
        """ Does the negate parameter work properly?"""
        res = self.log.filter("email", "has", "gmail.com", negate=True)
        self.assertIsInstance(res, gitnet.Log)
        self.assertNotIn('Alice', res)
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
                          "stars": [4, 5],
                          "age": 25},
                "Bobby": {"email": 'bobby@gmail.com',
                          "type": 'author',
                          "loc": 'Kitchener',
                          "books": ['BookC', 'BookD'],
                          "stars": [4, 4],
                          "age": 26}}
        self.log = gitnet.Log(data)

        # Setting up the directory for the tsv
        self.made_tsv = False
        try:
            self.tsv_str = self.log.tsv('temp.tsv')
            self.path = os.getcwd() + '/temp.tsv'
        finally:
            self.made_tsv = True

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
        tsv_str = self.log.tsv('temp.tsv')
        self.assertIsInstance(tsv_str, str)
        self.assertIn('t', tsv_str)

    def test_empty_cols(self):
        tsv_str = self.log.tsv('temp.tsv', empty_cols=True)
        # Checking file is created
        self.assertTrue(os.path.exists(self.path))
        # Check a summary string is produced
        self.assertEqual("Data written to temp.tsv", tsv_str)

    def test_warnings(self):
        # Warning occurs non string values are forced to strings
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            self.log.tsv('temp.tsv')
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
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

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
        sub.call(["rm", "-rf", ".git"])


class GenEdgesTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

        # Setting up the generator for edges
        self.edges = self.my_log.generate_edges(mode1='author', mode2='files')

    def test_basic(self):
        """ Is the correct data structure returned?"""
        self.assertIsInstance(self.edges, types.GeneratorType)
        self.assertIsInstance(self.edges.__next__(), tuple)

    def test_no_list(self):
        """ Does the method work when both modes occur as atomic values in the log?"""
        edges_rev = self.my_log.generate_edges(mode2='date', mode1='author')
        self.assertIsInstance(edges_rev, types.GeneratorType)
        self.assertIsInstance(edges_rev.__next__(), tuple)

    def test_values(self):
        """ Are the correct tuples contained within generate_edges()"""
        edge_list = []
        for e in self.edges:
            edge_list.append(e)

        # Check number of values
        self.assertEqual(len(edge_list), 11)

        # Check Marcela's edges
        edge_m6 = ("Marcela", "file6.md", {})
        edge_m7 = ("Marcela", "file6.md", {})
        self.assertIn(edge_m6, edge_list)
        self.assertIn(edge_m7, edge_list)

        # Check Billy G's edges
        edge_b4 = ("Billy G", "file4.md", {})
        edge_b5 = ("Billy G", "file5.md", {})
        edge_b6 = ("Billy G", "file6.md", {})
        self.assertIn(edge_b4, edge_list)
        self.assertIn(edge_b5, edge_list)
        self.assertIn(edge_b6, edge_list)

        # Check Jenna's edges
        edge_j3 = ("Jenna", "file3.md", {})
        edge_j5 = ("Jenna", "file5.md", {})
        self.assertIn(edge_j3, edge_list)
        self.assertIn(edge_j5, edge_list)

        # Check Randy's edges
        edge_r1 = ("Randy", "file1.md", {})
        edge_r2 = ("Randy", "file2.md", {})
        edge_r3 = ("Randy", "file3.md", {})
        edge_r4 = ("Randy", "file4.md", {})
        self.assertIn(edge_r1, edge_list)
        self.assertIn(edge_r2, edge_list)
        self.assertIn(edge_r3, edge_list)
        self.assertIn(edge_r4, edge_list)

    def test_attr(self):
        """ Does the method work correctly when edge attributes are given"""
        edges_attr = self.my_log.generate_edges(mode1='author', mode2='files', edge_attributes=['date', 'hash'])

        # Set up the list of tuples
        edge_list = []
        for e in edges_attr:
            edge_list.append(e)

        # Check the basics
        self.assertIsInstance(edges_attr, types.GeneratorType)
        self.assertIsInstance(edge_list[0], tuple)

        # Check number of values
        self.assertEqual(len(edge_list), 11)

        # Check Marcela's edges, tuples with date,tuple and tuple,date orders
        edge_m6dh = ("Marcela", "file6.md", {'date': 'Thu May 26 11:21:03 2016 -0400',
                                             'hash': '7965e62e1dda38c7f9d09684a17f5caef3f476f1'})
        edge_m6hd = ("Marcela", "file6.md", {'hash': '7965e62e1dda38c7f9d09684a17f5caef3f476f1',
                                             'date': 'Thu May 26 11:21:03 2016 -0400'})
        self.assertTrue(edge_m6dh in edge_list or edge_m6hd in edge_list)

        edge_m7dh = ("Marcela", "file6.md", {'date': 'Thu May 26 11:21:03 2016 -0400',
                                             'hash': '7965e62e1dda38c7f9d09684a17f5caef3f476f1'})
        edge_m7hd = ("Marcela", "file6.md", {'hash': '7965e62e1dda38c7f9d09684a17f5caef3f476f1',
                                             'date': 'Thu May 26 11:21:03 2016 -0400'})
        self.assertTrue(edge_m7dh in edge_list or edge_m7hd in edge_list)

        # Check Billy G's edges
        edge_b4dh = ("Billy G", "file4.md", {'date': 'Wed May 25 01:12:48 2016 -0400',
                                             'hash': '6cd4bbf82f41c504d5e3c10b99722e8955b648ed'})
        edge_b4hd = ("Billy G", "file4.md", {'hash': '6cd4bbf82f41c504d5e3c10b99722e8955b648ed',
                                             'date': 'Wed May 25 01:12:48 2016 -0400'})
        self.assertTrue(edge_b4dh in edge_list or edge_b4hd in edge_list)

        edge_b5dh = ("Billy G", "file5.md", {'date': 'Wed May 25 01:12:48 2016 -0400',
                                             'hash': '6cd4bbf82f41c504d5e3c10b99722e8955b648ed'})
        edge_b5hd = ("Billy G", "file5.md", {'hash': '6cd4bbf82f41c504d5e3c10b99722e8955b648ed',
                                             'date': 'Wed May 25 01:12:48 2016 -0400'})
        self.assertTrue(edge_b5dh in edge_list or edge_b5hd in edge_list)
        edge_b6dh = ("Billy G", "file6.md", {'date': 'Wed May 25 01:12:48 2016 -0400',
                                             'hash': '6cd4bbf82f41c504d5e3c10b99722e8955b648ed'})
        edge_b6hd = ("Billy G", "file6.md", {'hash': '6cd4bbf82f41c504d5e3c10b99722e8955b648ed',
                                             'date': 'Wed May 25 01:12:48 2016 -0400'})
        self.assertTrue(edge_b6dh in edge_list or edge_b6hd in edge_list)

        # Check Jenna's edges
        edge_j3dh = ("Jenna", "file3.md", {'date': 'Mon May 23 02:45:25 2016 -0400',
                                           'hash': 'ee2c408448eb1e0f735b95620bb433c453d026bc'})
        edge_j3hd = ("Jenna", "file3.md", {'hash': 'ee2c408448eb1e0f735b95620bb433c453d026bc',
                                           'date': 'Mon May 23 02:45:25 2016 -0400'})
        self.assertTrue(edge_j3dh in edge_list or edge_j3hd in edge_list)
        edge_j5dh = ("Jenna", "file5.md", {'date': 'Mon May 23 02:45:25 2016 -0400',
                                           'hash': 'ee2c408448eb1e0f735b95620bb433c453d026bc'})
        edge_j5hd = ("Jenna", "file5.md", {'hash': 'ee2c408448eb1e0f735b95620bb433c453d026bc',
                                           'date': 'Mon May 23 02:45:25 2016 -0400'})
        self.assertTrue(edge_j5dh in edge_list or edge_j5hd in edge_list)

        # Check Randy's edges
        edge_r1dh = ("Randy", "file1.md", {'date': 'Fri May 20 09:19:20 2016 -0400',
                                           'hash': 'b3a4bacaefb09236948b929eea29f346675f4ac2'})
        edge_r1hd = ("Randy", "file1.md", {'hash': 'b3a4bacaefb09236948b929eea29f346675f4ac2',
                                           'date': 'Fri May 20 09:19:20 2016 -0400'})
        self.assertTrue(edge_r1dh in edge_list or edge_r1hd in edge_list)
        edge_r2dh = ("Randy", "file2.md", {'date': 'Fri May 20 09:19:20 2016 -0400',
                                           'hash': 'b3a4bacaefb09236948b929eea29f346675f4ac2'})
        edge_r2hd = ("Randy", "file2.md", {'hash': 'b3a4bacaefb09236948b929eea29f346675f4ac2',
                                           'date': 'Fri May 20 09:19:20 2016 -0400'})
        self.assertTrue(edge_r2dh in edge_list or edge_r2hd in edge_list)
        edge_r3dh = ("Randy", "file3.md", {'date': 'Fri May 20 09:19:20 2016 -0400',
                                           'hash': 'b3a4bacaefb09236948b929eea29f346675f4ac2'})
        edge_r3hd = ("Randy", "file3.md", {'hash': 'b3a4bacaefb09236948b929eea29f346675f4ac2',
                                           'date': 'Fri May 20 09:19:20 2016 -0400'})
        self.assertTrue(edge_r3dh in edge_list or edge_r3hd in edge_list)

    def tearDown(self):
        # Delete the temporary .git folder
        sub.call(["rm", "-rf", ".git"])


class GenNodesTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

        # Setting up expected author tuples
        self.m_exp = ('Marcela', {'id': 'Marcela',
                                  'type': 'author',
                                  'records': ['7965e62']})
        self.b_exp = ('Billy G', {'id': 'Billy G',
                                  'type': 'author',
                                  'records': ['6cd4bbf']})
        self.j_exp = ('Jenna', {'id': 'Jenna',
                                'type': 'author',
                                'records': ['ee2c408']})
        self.r_exp = ('Randy', {'id': 'Randy',
                                'type': 'author',
                                'records': ['b3a4bac']})
        # Setting up expected file tuples. Note: because of lists, we only have set up nodes which have one hash record
        self.f1_exp = ('file1.md', {'id': 'file1.md',
                                    'type': 'files',
                                    'records': ['b3a4bac']})
        self.f2_exp = ('file2.md', {'id': 'file2.md',
                                    'type': 'files',
                                    'records': ['b3a4bac']})
        self.f7_exp = ('file7.md', {'id': 'file7.md',
                                    'type': 'files',
                                    'records': ['7965e62']})

    def test_basic(self):
        """Is a list of tuples returned?"""
        res = self.my_log.generate_nodes(mode1="author", mode2="files")
        # Correct length?
        self.assertEqual(len(res), 11)
        # List of Tuples?
        self.assertIsInstance(res, list)
        self.assertIsInstance(res.pop(), tuple)

    def test_default(self):
        """Using default attributes, does the method perform as expected?"""
        # Creating our list of tuples
        res = self.my_log.generate_nodes(mode1="author", mode2="files")

        # Checking authors
        self.assertIn(self.m_exp, res)
        self.assertIn(self.b_exp, res)
        self.assertIn(self.j_exp, res)
        self.assertIn(self.r_exp, res)

        # Checking files
        self.assertIn(self.f1_exp, res)
        self.assertIn(self.f2_exp, res)
        self.assertIn(self.f7_exp, res)

    def test_extra_atom(self):
        """Using extra attributes, does the method perform as expected?"""
        # Setting up expected author tuples
        m_exp = ('Marcela', {'id': 'Marcela',
                             'type': 'author',
                             'records': ['7965e62'],
                             'email': 'marcy@gmail.com'})
        b_exp = ('Billy G', {'id': 'Billy G',
                             'type': 'author',
                             'records': ['6cd4bbf'],
                             'email': 'bill@gmail.com'})
        j_exp = ('Jenna', {'id': 'Jenna',
                           'type': 'author',
                           'records': ['ee2c408'],
                           'email': 'jenna@gmail.com'})
        r_exp = ('Randy', {'id': 'Randy',
                           'type': 'author',
                           'records': ['b3a4bac'],
                           'email': 'randy@gmail.com'})

        # Setting up expected file tuples. Note: because of lists, we only have set up nodes which have one hash record
        f1_exp = ('file1.md', {'id': 'file1.md',
                               'type': 'files',
                               'records': ['b3a4bac'],
                               'email': 'randy@gmail.com'})
        f2_exp = ('file2.md', {'id': 'file2.md',
                               'type': 'files',
                               'records': ['b3a4bac'],
                               'email': 'randy@gmail.com'})
        f7_exp = ('file7.md', {'id': 'file7.md',
                               'type': 'files',
                               'records': ['7965e62'],
                               'email': 'marcy@gmail.com'})

        # Creating our list of tuples
        res_f = self.my_log.generate_nodes(mode1="files", mode2="author", keep_atom1=['email'])
        res_a = self.my_log.generate_nodes(mode1="files", mode2="author", keep_atom2=['email'])

        # Checking authors, which should have emails
        self.assertIn(m_exp, res_a)
        self.assertIn(b_exp, res_a)
        self.assertIn(j_exp, res_a)
        self.assertIn(r_exp, res_a)

        # Checking files, using defaults made in setUp
        self.assertIn(self.f1_exp, res_a)
        self.assertIn(self.f2_exp, res_a)
        self.assertIn(self.f7_exp, res_a)

        # Checking authors, using defaults made in setUp
        self.assertIn(self.m_exp, res_f)
        self.assertIn(self.b_exp, res_f)
        self.assertIn(self.j_exp, res_f)
        self.assertIn(self.r_exp, res_f)

        # Checking files, which should have emails
        self.assertIn(f1_exp, res_f)
        self.assertIn(f2_exp, res_f)
        self.assertIn(f7_exp, res_f)

    def test_extra_vect(self):
        # Setting up expected author tuples with vector attribute date
        m_exp = ('Marcela', {'id': 'Marcela',
                             'type': 'author',
                             'records': ['7965e62'],
                             'date': ['Thu May 26 11:21:03 2016 -0400']})
        b_exp = ('Billy G', {'id': 'Billy G',
                             'type': 'author',
                             'records': ['6cd4bbf'],
                             'date': ['Wed May 25 01:12:48 2016 -0400']})
        j_exp = ('Jenna', {'id': 'Jenna',
                           'type': 'author',
                           'records': ['ee2c408'],
                           'date': ['Mon May 23 02:45:25 2016 -0400']})
        r_exp = ('Randy', {'id': 'Randy',
                           'type': 'author',
                           'records': ['b3a4bac'],
                           'date': ['Fri May 20 09:19:20 2016 -0400']})

        # Setting up expected file tuples. Note: because of lists, we only have set up nodes which have one hash record
        f1_exp = ('file1.md', {'id': 'file1.md',
                               'type': 'files',
                               'records': ['b3a4bac'],
                               'date': ['Fri May 20 09:19:20 2016 -0400']})
        f2_exp = ('file2.md', {'id': 'file2.md',
                               'type': 'files',
                               'records': ['b3a4bac'],
                               'date': ['Fri May 20 09:19:20 2016 -0400']})
        f7_exp = ('file7.md', {'id': 'file7.md',
                               'type': 'files',
                               'records': ['7965e62'],
                               'date': ['Thu May 26 11:21:03 2016 -0400']})

        res_a = self.my_log.generate_nodes("author", "files", keep_vector1=["date"])
        res_f = self.my_log.generate_nodes("author", "files", keep_vector2=["date"])

        # Checking res_a
        # **************

        # Checking authors, which should have date lists
        self.assertIn(m_exp, res_a)
        self.assertIn(b_exp, res_a)
        self.assertIn(j_exp, res_a)
        self.assertIn(r_exp, res_a)

        # Checking files, using defaults made in setUp
        self.assertIn(self.f1_exp, res_a)
        self.assertIn(self.f2_exp, res_a)
        self.assertIn(self.f7_exp, res_a)

        # Checking res_f
        # **************

        # Checking authors, using defaults made in setUp
        self.assertIn(self.m_exp, res_f)
        self.assertIn(self.b_exp, res_f)
        self.assertIn(self.j_exp, res_f)
        self.assertIn(self.r_exp, res_f)

        # Checking files, which should have date lists
        self.assertIn(f1_exp, res_f)
        self.assertIn(f2_exp, res_f)
        self.assertIn(f7_exp, res_f)

        # FLIPPING FILES & AUTHOR
        # ***********************

        res_a = self.my_log.generate_nodes("files", "author", keep_vector2=["date"])
        res_f = self.my_log.generate_nodes("files", "author", keep_vector1=["date"])

        # Checking res_a
        # **************

        # Checking authors, which should have date lists
        self.assertIn(m_exp, res_a)
        self.assertIn(b_exp, res_a)
        self.assertIn(j_exp, res_a)
        self.assertIn(r_exp, res_a)

        # Checking files, using defaults made in setUp
        self.assertIn(self.f1_exp, res_a)
        self.assertIn(self.f2_exp, res_a)
        self.assertIn(self.f7_exp, res_a)

        # Checking res_f
        # **************

        # Checking authors, using defaults made in setUp
        self.assertIn(self.m_exp, res_f)
        self.assertIn(self.b_exp, res_f)
        self.assertIn(self.j_exp, res_f)
        self.assertIn(self.r_exp, res_f)

        # Checking files, which should have date lists
        self.assertIn(f1_exp, res_f)
        self.assertIn(f2_exp, res_f)
        self.assertIn(f7_exp, res_f)

    def test_author_email(self):
        """Does the method work when both modes are atomic in the log?"""
        # Create list of tuples
        res = self.my_log.generate_nodes(mode1="email", mode2="author")

        # Check type
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], tuple)

        # Check authors
        self.assertIn(self.m_exp, res)
        self.assertIn(self.b_exp, res)
        self.assertIn(self.j_exp, res)
        self.assertIn(self.r_exp, res)

        # Check emails
        email_m = ('marcy@gmail.com', {'id': 'marcy@gmail.com',
                                       'type': 'email',
                                       'records': ['7965e62']})
        email_b = ('bill@gmail.com', {'id': 'bill@gmail.com',
                                       'type': 'email',
                                       'records': ['6cd4bbf']})
        email_j = ('jenna@gmail.com', {'id': 'jenna@gmail.com',
                                       'type': 'email',
                                       'records': ['ee2c408']})
        email_r = ('randy@gmail.com', {'id': 'randy@gmail.com',
                                       'type': 'email',
                                       'records': ['b3a4bac']})
        self.assertIn(email_m, res)
        self.assertIn(email_b, res)
        self.assertIn(email_j, res)
        self.assertIn(email_r, res)

    def test_warnings(self):
        """Does a warning occur when invalid tags are given?"""
        # Warning occurs when dates are compared using <,<=,>,>= functions
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            self.my_log.generate_nodes(mode1="dogs", mode2="cats")
            # Check Warning occurred
            self.assertEqual(len(w), 1)
            self.assertIn("Dictionary of node attributes is empty. Check that mode1 and mode2 names are valid tags.",
                          str(w[-1].message))

    def tearDown(self):
        sub.call(["rm","-rf",".git"])


class GenNetworkTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

        self.graph = self.my_log.generate_network(mode1='author', mode2='files', edge_attributes=['date'])

    def test_basic(self):
        """Does the method produce a MultiGraphPlus object?"""
        self.assertIsInstance(self.graph, gitnet.MultiGraphPlus)
        self.assertEqual(self.graph.mode1, "author")
        self.assertEqual(self.graph.mode2, "files")

    def test_nodes(self):
        """Are the correct nodes recorded in the network?"""
        mg = self.graph
        # Are there the correct number of nodes?
        self.assertEqual(len(mg.nodes()), 11)

        # Checking the author nodes
        self.assertDictEqual(mg.node['Marcela'], {'id': 'Marcela',
                                                  'type': 'author',
                                                  'records': ['7965e62']})
        self.assertDictEqual(mg.node['Billy G'], {'id': 'Billy G',
                                                  'type': 'author',
                                                  'records': ['6cd4bbf']})
        self.assertDictEqual(mg.node['Jenna'], {'id': 'Jenna',
                                                'type': 'author',
                                                'records': ['ee2c408']})
        self.assertDictEqual(mg.node['Randy'], {'id': 'Randy',
                                                'type': 'author',
                                                'records': ['b3a4bac']})

        # Checking the file nodes
        self.assertDictEqual(mg.node['file1.md'], {'id': 'file1.md',
                                                   'type': 'files',
                                                   'records': ['b3a4bac']})
        self.assertDictEqual(mg.node['file2.md'], {'id': 'file2.md',
                                                   'type': 'files',
                                                   'records': ['b3a4bac']})
        self.assertTrue(mg.node['file3.md'] == {'id': 'file3.md',
                                                'type': 'files',
                                                'records': ['b3a4bac', 'ee2c408']} or
                        mg.node['file3.md'] == {'id': 'file3.md',
                                                'type': 'files',
                                                'records': ['ee2c408', 'b3a4bac']})
        self.assertTrue(mg.node['file4.md'] == {'id': 'file4.md',
                                                'type': 'files',
                                                'records': ['b3a4bac', '6cd4bbf']} or
                        mg.node['file4.md'] == {'id': 'file4.md',
                                                'type': 'files',
                                                'records': ['6cd4bbf', 'b3a4bac']})
        self.assertTrue(mg.node['file5.md'] == {'id': 'file5.md',
                                                'type': 'files',
                                                'records': ['6cd4bbf', 'ee2c408']} or
                        mg.node['file5.md'] == {'id': 'file5.md',
                                                'type': 'files',
                                                'records': ['ee2c408', '6cd4bbf']})
        self.assertTrue(mg.node['file6.md'] == {'id': 'file6.md',
                                                'type': 'files',
                                                'records': ['6cd4bbf', '7965e62']} or
                        mg.node['file6.md'] == {'id': 'file6.md',
                                                'type': 'files',
                                                'records': ['7965e62', '6cd4bbf']})
        self.assertDictEqual(mg.node['file7.md'], {'id': 'file7.md',
                                                   'type': 'files',
                                                   'records': ['7965e62']})

    def test_edges(self):
        """Are the correct edges contained in the network"""
        mg = self.graph

        # Checking the correct number of edges are in the network
        self.assertEqual(len(self.graph.edges()), 11)

        self.assertDictEqual(mg.edge['Marcela']['file7.md'], {0: {'date': 'Thu May 26 11:21:03 2016 -0400'}})
        self.assertDictEqual(mg.edge['Marcela']['file6.md'], {0: {'date': 'Thu May 26 11:21:03 2016 -0400'}})
        self.assertDictEqual(mg.edge['Billy G']['file4.md'], {0: {'date': 'Wed May 25 01:12:48 2016 -0400'}})
        self.assertDictEqual(mg.edge['Billy G']['file5.md'], {0: {'date': 'Wed May 25 01:12:48 2016 -0400'}})
        self.assertDictEqual(mg.edge['Billy G']['file6.md'], {0: {'date': 'Wed May 25 01:12:48 2016 -0400'}})
        self.assertDictEqual(mg.edge['Jenna']['file3.md'], {0: {'date': 'Mon May 23 02:45:25 2016 -0400'}})
        self.assertDictEqual(mg.edge['Jenna']['file5.md'], {0: {'date': 'Mon May 23 02:45:25 2016 -0400'}})
        self.assertDictEqual(mg.edge['Randy']['file1.md'], {0: {'date': 'Fri May 20 09:19:20 2016 -0400'}})
        self.assertDictEqual(mg.edge['Randy']['file2.md'], {0: {'date': 'Fri May 20 09:19:20 2016 -0400'}})
        self.assertDictEqual(mg.edge['Randy']['file3.md'], {0: {'date': 'Fri May 20 09:19:20 2016 -0400'}})
        self.assertDictEqual(mg.edge['Randy']['file4.md'], {0: {'date': 'Fri May 20 09:19:20 2016 -0400'}})

    def tearDown(self):
        # Delete temporary .git file
        sub.call(["rm", "-rf", ".git"])


class WriteEdgesTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

        # Setting up the written nodes file
        self.made_edges = False
        try:
            self.res = self.my_log.write_edges("temp_edges.txt", mode1="author", mode2="files", edge_attribute=[])
            self.path = os.getcwd() + '/temp_edges.txt'
        finally:
            self.made_edges = True

    def test_basic(self):
        """Does the test return None, but still create a file?"""
        # Check return value is None
        self.assertIsNone(self.res)
        # Check new file exists where expected
        self.assertTrue(os.path.exists(self.path))

    def test_no_attr(self):
        """Are the correct values being outputted to the file when no attributes are given?"""
        f = open("temp_edges.txt", "r")
        f_str = f.read()

        # Check Type
        self.assertIsInstance(f_str, str)

        # Check Header
        self.assertIn("id1,id2\n", f_str)

        # Check contents
        self.assertIn("Marcela,file6.md\n", f_str)
        self.assertIn("Marcela,file7.md\n", f_str)
        self.assertIn("Billy G,file4.md\n", f_str)
        self.assertIn("Billy G,file5.md\n", f_str)
        self.assertIn("Billy G,file6.md\n", f_str)
        self.assertIn("Jenna,file3.md\n", f_str)
        self.assertIn("Jenna,file5.md\n", f_str)
        self.assertIn("Randy,file1.md\n", f_str)
        self.assertIn("Randy,file2.md\n", f_str)
        self.assertIn("Randy,file3.md\n", f_str)
        self.assertIn("Randy,file4.md\n", f_str)

        # Close file
        f.close()

    def test_default(self):
        """Do the defaults include weight and date as edge_attributes?"""
        res = self.my_log.write_edges("temp_edges.txt", mode1="author", mode2="files")
        f = open("temp_edges.txt", "r")
        f_str = f.read()

        # Check Types
        self.assertIsNone(res)
        self.assertIsInstance(f_str, str)

        # Check Header
        self.assertIn("id1,id2,weight,date\n", f_str)

        # Check contents
        self.assertIn("Marcela,file6.md,NA,5-26-2016\n", f_str)
        self.assertIn("Marcela,file7.md,NA,5-26-2016\n", f_str)
        self.assertIn("Billy G,file4.md,NA,5-25-2016\n", f_str)
        self.assertIn("Billy G,file5.md,NA,5-25-2016\n", f_str)
        self.assertIn("Billy G,file6.md,NA,5-25-2016\n", f_str)
        self.assertIn("Jenna,file3.md,NA,5-23-2016\n", f_str)
        self.assertIn("Jenna,file5.md,NA,5-23-2016\n", f_str)
        self.assertIn("Randy,file1.md,NA,5-20-2016\n", f_str)
        self.assertIn("Randy,file2.md,NA,5-20-2016\n", f_str)
        self.assertIn("Randy,file3.md,NA,5-20-2016\n", f_str)
        self.assertIn("Randy,file4.md,NA,5-20-2016\n", f_str)

        # Close file
        f.close()

    def test_attrs(self):
        """Does the method work when extra attributes are included?"""
        res = self.my_log.write_edges("temp_edges.txt", mode1="author", mode2="files",
                                      edge_attribute=['date','hash', 'email'])
        f = open("temp_edges.txt", "r")
        f_str = f.read()

        # Check Types
        self.assertIsNone(res)
        self.assertIsInstance(f_str, str)

        # Check Header
        self.assertIn("id1,id2,date,hash,email\n", f_str)

        # Check contents
        self.assertIn("Marcela,file6.md,5-26-2016,7965e62e1dda38c7f9d09684a17f5caef3f476f1,marcy@gmail.com\n", f_str)
        self.assertIn("Marcela,file7.md,5-26-2016,7965e62e1dda38c7f9d09684a17f5caef3f476f1,marcy@gmail.com\n", f_str)
        self.assertIn("Billy G,file4.md,5-25-2016,6cd4bbf82f41c504d5e3c10b99722e8955b648ed,bill@gmail.com\n", f_str)
        self.assertIn("Billy G,file5.md,5-25-2016,6cd4bbf82f41c504d5e3c10b99722e8955b648ed,bill@gmail.com\n", f_str)
        self.assertIn("Billy G,file6.md,5-25-2016,6cd4bbf82f41c504d5e3c10b99722e8955b648ed,bill@gmail.com\n", f_str)
        self.assertIn("Jenna,file3.md,5-23-2016,ee2c408448eb1e0f735b95620bb433c453d026bc,jenna@gmail.com\n", f_str)
        self.assertIn("Jenna,file5.md,5-23-2016,ee2c408448eb1e0f735b95620bb433c453d026bc,jenna@gmail.com\n", f_str)
        self.assertIn("Randy,file1.md,5-20-2016,b3a4bacaefb09236948b929eea29f346675f4ac2,randy@gmail.com\n", f_str)
        self.assertIn("Randy,file2.md,5-20-2016,b3a4bacaefb09236948b929eea29f346675f4ac2,randy@gmail.com\n", f_str)
        self.assertIn("Randy,file3.md,5-20-2016,b3a4bacaefb09236948b929eea29f346675f4ac2,randy@gmail.com\n", f_str)
        self.assertIn("Randy,file4.md,5-20-2016,b3a4bacaefb09236948b929eea29f346675f4ac2,randy@gmail.com\n", f_str)

        # Close file
        f.close()

    def tearDown(self):
        # Delete the temporary .git folder
        sub.call(["rm", "-rf", ".git"])

        # Delete our temporary written edges file
        if self.made_edges:
            sub.call(['rm', 'temp_edges.txt'])


class WriteNodesTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

        # Setting up the written nodes file
        self.made_nodes = False
        try:
            self.res = self.my_log.write_nodes(fname='temp_node.txt', mode1="author", mode2="files",
                                               keep_atom1=['email'], keep_vector1=['records'])
            self.path = os.getcwd() + '/temp_node.txt'
        finally:
            self.made_nodes = True

    def test_basic(self):
        """Does the method return nothing, but create a new file?"""
        # Check return value is None
        self.assertIsNone(self.res)
        # Check new file exists where expected
        self.assertTrue(os.path.exists(self.path))

    def test_values(self):
        """Are the correct values being outputted to the file?"""
        f = open("temp_node.txt", "r")
        f_str = f.read()
        self.assertIsInstance(f_str, str)
        # Check Header
        self.assertIn("hashid,id,type,email,records", f_str)
        # Check Authors
        self.assertIn("Marcela,author,marcy@gmail.com,7965e62", f_str)
        self.assertIn("Billy G,author,bill@gmail.com,6cd4bbf", f_str)
        self.assertIn("Jenna,author,jenna@gmail.com,ee2c408", f_str)
        self.assertIn("Randy,author,randy@gmail.com,b3a4bac", f_str)
        # Check files
        self.assertIn("file1.md,files,NA,b3a4bac", f_str)
        self.assertIn("file2.md,files,NA,b3a4bac", f_str)
        self.assertTrue("file3.md,files,NA,ee2c408;b3a4bac" in f_str or
                        "file3.md,files,NA,b3a4bac;ee2c408" in f_str)
        self.assertTrue("file4.md,files,NA,6cd4bbf;b3a4bac" in f_str or
                        "file4.md,files,NA,b3a4bac;6cd4bbf" in f_str)
        self.assertTrue("file5.md,files,NA,ee2c408;6cd4bbf" in f_str or
                        "file5.md,files,NA,6cd4bbf;ee2c408" in f_str)
        self.assertTrue("file6.md,files,NA,6cd4bbf;7965e62" in f_str or
                        "file6.md,files,NA,7965e62;6cd4bbf" in f_str)
        self.assertIn("file7.md,files,NA,7965e62", f_str)
        # Close File
        f.close()

    def tearDown(self):
        # Delete the temporary .git folder
        sub.call(["rm", "-rf", ".git"])
        # Delete our temporary written nodes file
        if self.made_nodes:
            sub.call(['rm', 'temp_node.txt'])


if __name__ == '__main__':
    unittest.main(buffer=True)
