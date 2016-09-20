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

import gitnet
import unittest
import subprocess as sub
import os
from unittest.mock import patch
from io import StringIO
from gitnet.exceptions import InputError


class GetTagsTests(unittest.TestCase):

    def test_basic(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        path = os.getcwd()
        my_log = gitnet.get_log(path)

        tags = my_log.get_tags()

        self.assertListEqual(tags, ["hash", "author", "email", "domain", "date", "utc_date", "utc_datetime", "mode", "merge",
                                    "summary", "fedits", "inserts", "deletes", "message", "files", "changes"])

        # Delete temporary .git file
        sub.call(["rm", "-rf", ".git"])

class AnnotateTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        path = os.getcwd()
        self.my_log = gitnet.get_log(path)

    def test_utc_date(self):
        """Is utc_date being generated correctly?"""
        self.assertEqual(self.my_log["7965e62"]["utc_date"],"2016-05-26")
        self.assertEqual(self.my_log["6cd4bbf"]["utc_date"],"2016-05-25")
        self.assertEqual(self.my_log["ee2c408"]["utc_date"],"2016-05-23")
        self.assertEqual(self.my_log["b3a4bac"]["utc_date"],"2016-05-20")

    def test_utc_datetime(self):
        """Is utc_datetime being generated correctly?"""
        self.assertEqual(self.my_log["7965e62"]["utc_datetime"],"2016-05-26 15:21:03")
        self.assertEqual(self.my_log["6cd4bbf"]["utc_datetime"],"2016-05-25 05:12:48")
        self.assertEqual(self.my_log["ee2c408"]["utc_datetime"],"2016-05-23 06:45:25")
        self.assertEqual(self.my_log["b3a4bac"]["utc_datetime"],"2016-05-20 13:19:20")

    def test_domain(self):
        """Is domain being generated correctly?"""
        self.assertEqual(self.my_log["7965e62"]["domain"],"gmail")
        self.assertEqual(self.my_log["6cd4bbf"]["domain"],"gmail")
        self.assertEqual(self.my_log["ee2c408"]["domain"],"gmail")
        self.assertEqual(self.my_log["b3a4bac"]["domain"],"gmail")

    def tearDown(self):
        # Delete temporary .git file
        sub.call(["rm", "-rf", ".git"])

class DescribeTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        path = os.getcwd()
        self.my_log = gitnet.get_log(path)

    def test_basic(self):
        """Is there something being printed to the screen?"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            ret = self.my_log.describe()
            self.assertIsNone(ret)
            self.assertNotEqual(fake_out.getvalue(), "")

    def test_default(self):
        """Does the default method print the proper information?"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.my_log.describe(mode="default")
            output = fake_out.getvalue()
            self.assertIn("Log containing 4 records from local git created at ", output)
            self.assertIn("\nOrigin:", output)
            self.assertNotIn("Filters:", output)
            self.assertIn("\nNumber of authors: 4\n", output)
            self.assertIn("\nNumber of files: 7\n", output)
            self.assertIn("\nMost common email address domains:", output)
            self.assertIn("\n\t @gmail.com [4 users]\n", output)
            self.assertIn("\nDate range: 2016-05-20 09:19:20-04:00 to 2016-05-26 11:21:03-04:00\n", output)
            self.assertIn("\nChange distribution summary:\n", output)
            self.assertIn("\n\t Files changed: Mean = 2.75, SD = 0.829\n", output)
            self.assertIn("\n\t Line insertions: Mean = 2.75, SD = 0.829\n", output)
            self.assertIn("\n\t Line deletions: Mean = nan, SD = nan\n", output)
            self.assertIn("\nNumber of merges: 0\n", output)
            self.assertIn("\nNumber of parsing errors: 0\n", output)

    def test_not_default(self):
        """ Does a non-default method print the proper information?
            Note: At this point, default is the only setting so they end up being the same."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.my_log.describe(mode="not default")
            output = fake_out.getvalue()
            self.assertIn("Log containing 4 records from local git created at ", output)
            self.assertIn("\nOrigin:", output)
            self.assertNotIn("Filters:", output)
            self.assertIn("\nNumber of authors: 4\n", output)
            self.assertIn("\nNumber of files: 7\n", output)
            self.assertIn("\nMost common email address domains:", output)
            self.assertIn("\n\t @gmail.com [4 users]\n", output)
            self.assertIn("\nDate range: 2016-05-20 09:19:20-04:00 to 2016-05-26 11:21:03-04:00\n", output)
            self.assertIn("\nChange distribution summary:\n", output)
            self.assertIn("\n\t Files changed: Mean = 2.75, SD = 0.829\n", output)
            self.assertIn("\n\t Line insertions: Mean = 2.75, SD = 0.829\n", output)
            self.assertIn("\n\t Line deletions: Mean = nan, SD = nan\n", output)
            self.assertIn("\nNumber of merges: 0\n", output)
            self.assertIn("\nNumber of parsing errors: 0\n", output)

    def test_whole(self):
        """Is the entire output as expected?"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.my_log.describe()
            out = fake_out.getvalue()

            self.assertRegex(out, "Log containing 4 records from local git created at ....-..-.. ..:..:..\.......\.\n"
                                  "Origin:  .*\n"
                                  "Number of authors: 4\n"
                                  "Number of files: 7\n"
                                  "Most common email address domains:\n"
                                  "\t @gmail.com \[4 users\]\n"
                                  "Date range: 2016-05-20 09:19:20-04:00 to 2016-05-26 11:21:03-04:00\n"
                                  "Change distribution summary:\n"
                                  "\t Files changed: Mean = 2.75, SD = 0.829\n"
                                  "\t Line insertions: Mean = 2.75, SD = 0.829\n"
                                  "\t Line deletions: Mean = nan, SD = nan\n"
                                  "Number of merges: 0\n"
                                  "Number of parsing errors: 0\n")

    def test_exclude(self):
        """Does exclude prevent statistics from being printed?"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.my_log.describe(exclude=['merges', 'errors', 'files', 'summary', 'changes', 'path', 'filters',
                                          'authors', 'dates', 'emails'])
            output = fake_out.getvalue()
            self.assertNotIn("Log containing 4 records from local git created at ", output)
            self.assertNotIn("\nOrigin:", output)
            self.assertNotIn("Filters:", output)
            self.assertNotIn("\nNumber of authors: 4\n", output)
            self.assertNotIn("\nNumber of files: 7\n", output)
            self.assertNotIn("\nMost common email address domains:", output)
            self.assertNotIn("\n\t @gmail.com [4 users]\n", output)
            self.assertNotIn("\nDate range: 2016-05-20 09:19:20-04:00 to 2016-05-26 11:21:03-04:00\n", output)
            self.assertNotIn("\nChange distribution summary:\n", output)
            self.assertNotIn("\n\t Files changed: Mean = 2.75, SD = 0.829\n", output)
            self.assertNotIn("\n\t Line insertions: Mean = 2.75, SD = 0.829\n", output)
            self.assertNotIn("\n\t Line deletions: Mean = nan, SD = nan\n", output)
            self.assertNotIn("\nNumber of merges: 0\n", output)
            self.assertNotIn("\nNumber of parsing errors: 0\n", output)
            self.assertEqual(output, "")

    def test_filters(self):
        """Are the correct results obtained when the log has been filtered?"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            log = self.my_log.filter("author", "equals", "Randy", negate=True)
            log.describe()
            output = fake_out.getvalue()
            self.assertIn("Log containing 3 records from local git created at ", output)
            self.assertIn("\nOrigin:", output)
            self.assertIn("Filters:\n", output)
            self.assertIn("\t author equals Randy | Negate: True | Helper: None\n", output)
            self.assertIn("\nNumber of authors: 3\n", output)
            self.assertIn("\nNumber of files: 5\n", output)
            self.assertIn("\nMost common email address domains:", output)
            self.assertIn("\n\t @gmail.com [3 users]\n", output)
            self.assertIn("\nDate range: 2016-05-23 02:45:25-04:00 to 2016-05-26 11:21:03-04:00\n", output)
            self.assertIn("\nChange distribution summary:\n", output)
            self.assertIn("\n\t Files changed: Mean = 2.333, SD = 0.471\n", output)
            self.assertIn("\n\t Line insertions: Mean = 2.333, SD = 0.471\n", output)
            self.assertIn("\n\t Line deletions: Mean = nan, SD = nan\n", output)
            self.assertIn("\nNumber of merges: 0\n", output)
            self.assertIn("\nNumber of parsing errors: 0\n", output)

    def test_changes(self):
        """Are changes to files such as merge and delete displayed?"""
        # Setting up a more complicated repository
        sub.call(["rm", "-rf", ".git"])
        sub.call(["cp", "-R", "repo_nx.git", ".git"])
        path = os.getcwd()
        nx_log = gitnet.get_log(path)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            nx_log.describe()
            output = fake_out.getvalue()
            self.assertIsInstance(output, str)
            self.assertIn("Log containing 4881 records from local git created at ", output)
            self.assertIn("\nOrigin:", output)
            self.assertNotIn("Filters:", output)
            self.assertIn("\nNumber of authors: 181\n", output)
            self.assertIn("\nNumber of files: 1559\n", output)
            self.assertIn("\nMost common email address domains:", output)
            self.assertIn("\n\t @gmail.com [89 users]\n", output)
            self.assertIn("\n\t @users.noreply.github.com [8 users]\n", output)
            self.assertIn("\n\t @ucl.ac.uk [2 users]\n", output)
            self.assertIn("\n\t @hotmail.com [2 users]\n", output)
            self.assertIn("\nDate range: 2005-07-12 23:35:35+00:00 to 2016-05-18 21:46:13-04:00\n", output)
            self.assertIn("\nChange distribution summary:\n", output)
            self.assertIn("\n\t Files changed: Mean = 2.621, SD = 8.727", output)
            self.assertIn("\n\t Line insertions: Mean = 103.837, SD = 1082.744\n", output)
            self.assertIn("\n\t Line deletions: Mean = 77.315, SD = 870.92\n", output)
            self.assertIn("\nNumber of merges: 798\n", output)
            self.assertIn("\nNumber of parsing errors: 0\n", output)

    def tearDown(self):
        # Delete temporary .git file
        sub.call(["rm", "-rf", ".git"])


class IgnoreTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        path = os.getcwd()
        self.my_log = gitnet.get_log(path)
        self.ignore_all = self.my_log.ignore(".*.md")
        self.ignore_one = self.my_log.ignore("file1.md")

    def test_basic(self):
        """Is a new equal sized commit log returned?"""
        self.assertIsInstance(self.ignore_one, gitnet.CommitLog)
        self.assertEqual(len(self.ignore_all), len(self.my_log))
        self.assertEqual(len(self.ignore_one), len(self.my_log))

        # Check that when a network is created, there are no edges
        net = self.ignore_all.generate_network(mode1='author', mode2='files')
        self.assertEqual(len(net.edges()), 0)

    def test_simp_values(self):
        """Are the appropriate files being removed with simple ignore?"""
        self.assertSetEqual(set(self.my_log.vector('files')), {'file1.md', 'file2.md', 'file3.md', 'file4.md',
                                                               'file5.md', 'file6.md', 'file7.md'})
        self.assertSetEqual(set(self.ignore_one.vector('files')), {'file2.md', 'file3.md', 'file4.md',
                                                                   'file5.md', 'file6.md', 'file7.md'})
        self.assertSetEqual(set(self.ignore_all.vector('files')), set([]))

    def test_no_match(self):
        """Does the method behave properly when ignore is 'no match'?"""
        ignore_none = self.my_log.ignore(".*.md", ignoreif="no match")
        self.assertSetEqual(set(ignore_none.vector('files')), {'file1.md', 'file2.md', 'file3.md', 'file4.md',
                                                               'file5.md', 'file6.md', 'file7.md'})
        ignore_all_but1 = self.my_log.ignore("file1.md", ignoreif="no match")
        self.assertSetEqual(set(ignore_all_but1.vector('files')), {'file1.md'})

    def tearDown(self):
        # Delete temporary .git file
        sub.call(["rm", "-rf", ".git"])


class NetworkTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

        self.simp_net = self.my_log.network(type="author/file/simple")

    def test_basic(self):
        """ Is a MultiGraphPlus Object returned?"""
        self.assertIsInstance(self.simp_net, gitnet.MultiGraphPlus)

    def test_author_file_simple(self):
        simp_net = self.simp_net

        # Checking the author nodes
        self.assertDictEqual(simp_net.node['Marcela'], {'id': 'Marcela',
                                                        'type': 'author',
                                                        'records': ['7965e62']})
        self.assertDictEqual(simp_net.node['Billy G'], {'id': 'Billy G',
                                                        'type': 'author',
                                                        'records': ['6cd4bbf']})
        self.assertDictEqual(simp_net.node['Jenna'], {'id': 'Jenna',
                                                      'type': 'author',
                                                      'records': ['ee2c408']})
        self.assertDictEqual(simp_net.node['Randy'], {'id': 'Randy',
                                                      'type': 'author',
                                                      'records': ['b3a4bac']})
        # Checking the file nodes
        self.assertDictEqual(simp_net.node['file1.md'], {'id': 'file1.md',
                                                         'type': 'files',
                                                         'records': ['b3a4bac']})
        self.assertDictEqual(simp_net.node['file2.md'], {'id': 'file2.md',
                                                         'type': 'files',
                                                         'records': ['b3a4bac']})
        self.assertTrue(simp_net.node['file3.md'] == {'id': 'file3.md',
                                                      'type': 'files',
                                                      'records': ['b3a4bac', 'ee2c408']} or
                        simp_net.node['file3.md'] == {'id': 'file3.md',
                                                      'type': 'files',
                                                      'records': ['ee2c408', 'b3a4bac']})
        self.assertTrue(simp_net.node['file4.md'] == {'id': 'file4.md',
                                                      'type': 'files',
                                                      'records': ['b3a4bac', '6cd4bbf']} or
                        simp_net.node['file4.md'] == {'id': 'file4.md',
                                                      'type': 'files',
                                                      'records': ['6cd4bbf', 'b3a4bac']})
        self.assertTrue(simp_net.node['file5.md'] == {'id': 'file5.md',
                                                      'type': 'files',
                                                      'records': ['6cd4bbf', 'ee2c408']} or
                        simp_net.node['file5.md'] == {'id': 'file5.md',
                                                      'type': 'files',
                                                      'records': ['ee2c408', '6cd4bbf']})
        self.assertTrue(simp_net.node['file6.md'] == {'id': 'file6.md',
                                                      'type': 'files',
                                                      'records': ['6cd4bbf', '7965e62']} or
                        simp_net.node['file6.md'] == {'id': 'file6.md',
                                                      'type': 'files',
                                                      'records': ['7965e62', '6cd4bbf']})
        self.assertDictEqual(simp_net.node['file7.md'], {'id': 'file7.md',
                                                         'type': 'files',
                                                         'records': ['7965e62']})

        # Check the edges
        self.assertDictEqual(simp_net.edge['Marcela']['file7.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Marcela']['file6.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Billy G']['file4.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Billy G']['file5.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Billy G']['file6.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Jenna']['file3.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Jenna']['file5.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Randy']['file1.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Randy']['file2.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Randy']['file3.md'], {0: {}})
        self.assertDictEqual(simp_net.edge['Randy']['file4.md'], {0: {}})

    def test_author_file(self):
        aut_file = self.my_log.network(type="author/file")

        auth_list = ['Marcela', 'Billy G', 'Jenna', 'Randy']
        for a in auth_list:
            self.assertIn('id', aut_file.node[a])
            self.assertIn('type', aut_file.node[a])
            self.assertEqual(aut_file.node[a]['type'], 'author')
            self.assertIn('records', aut_file.node[a])
            self.assertIn('email', aut_file.node[a])
            self.assertIn('hash', aut_file.node[a])
            self.assertIn('fedits', aut_file.node[a])
            self.assertNotIn('weight', aut_file.node[a])
            self.assertNotIn('date', aut_file.node[a])

        file_list = ['file1.md', 'file2.md', 'file3.md', 'file4.md', 'file5.md', 'file6.md', 'file7.md']
        for f in file_list:
            self.assertIn('id', aut_file.node[f])
            self.assertIn('type', aut_file.node[f])
            self.assertEqual(aut_file.node[f]['type'], 'files')
            self.assertIn('records', aut_file.node[f])
            self.assertIn('hash', aut_file.node[f])
            self.assertIn('date', aut_file.node[f])
            self.assertNotIn('email', aut_file.node[f])
            self.assertNotIn('fedits', aut_file.node[f])
            self.assertNotIn('weight', aut_file.node[f])

        edge_list = [('Marcela', 'file7.md'), ('Marcela', 'file6.md'),
                     ('Billy G', 'file4.md'), ('Billy G', 'file5.md'), ('Billy G', 'file6.md'),
                     ('Jenna', 'file3.md'), ('Jenna', 'file5.md'),
                     ('Randy', 'file1.md'), ('Randy', 'file2.md'), ('Randy', 'file3.md'), ('Randy', 'file4.md'),]

        for n1, n2 in edge_list:
            self.assertIn('author', aut_file.edge[n1][n2][0])
            self.assertIn('hash', aut_file.edge[n1][n2][0])
            self.assertNotIn('date', aut_file.edge[n1][n2][0])
            self.assertEqual(len(aut_file.edge[n1][n2]), 1)
            self.assertEqual(len(aut_file.edge[n1][n2][0]), 2)

    def test_author_file_weighted(self):
        weighted = self.my_log.network(type="author/file/weighted")

        auth_list = ['Marcela', 'Billy G', 'Jenna', 'Randy']
        for a in auth_list:
            self.assertIn('id', weighted.node[a])
            self.assertIn('type', weighted.node[a])
            self.assertEqual(weighted.node[a]['type'], 'author')
            self.assertIn('records', weighted.node[a])
            self.assertIn('email', weighted.node[a])
            self.assertIn('hash', weighted.node[a])
            self.assertIn('fedits', weighted.node[a])
            self.assertNotIn('weight', weighted.node[a])
            self.assertNotIn('date', weighted.node[a])

        file_list = ['file1.md', 'file2.md', 'file3.md', 'file4.md', 'file5.md', 'file6.md', 'file7.md']
        for f in file_list:
            self.assertIn('id', weighted.node[f])
            self.assertIn('type', weighted.node[f])
            self.assertEqual(weighted.node[f]['type'], 'files')
            self.assertIn('records', weighted.node[f])
            self.assertIn('hash', weighted.node[f])
            self.assertIn('date', weighted.node[f])
            self.assertNotIn('email', weighted.node[f])
            self.assertNotIn('fedits', weighted.node[f])
            self.assertNotIn('weight', weighted.node[f])

        edge_list = [('Marcela', 'file7.md'), ('Marcela', 'file6.md'),
                     ('Billy G', 'file4.md'), ('Billy G', 'file5.md'), ('Billy G', 'file6.md'),
                     ('Jenna', 'file3.md'), ('Jenna', 'file5.md'),
                     ('Randy', 'file1.md'), ('Randy', 'file2.md'), ('Randy', 'file3.md'), ('Randy', 'file4.md'), ]

        for n1, n2 in edge_list:
            self.assertIn('author', weighted.edge[n1][n2][0])
            self.assertIn('hash', weighted.edge[n1][n2][0])
            self.assertIn('date', weighted.edge[n1][n2][0])
            self.assertIn('weight', weighted.edge[n1][n2][0])
            self.assertEqual(len(weighted.edge[n1][n2]), 1)
            self.assertEqual(len(weighted.edge[n1][n2][0]), 4)

    def test_error(self):
        with self.assertRaisesRegex(InputError, 'nonsense is not a valid network preset.'):
            self.my_log.network(type="nonsense")

    def tearDown(self):
        # Delete temporary .git file
        sub.call(["rm", "-rf", ".git"])


if __name__ == '__main__':
    unittest.main(buffer=True)
