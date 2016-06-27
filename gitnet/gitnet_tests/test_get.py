# Written by Jillain Anderson, Joel Becker, and Steve McColl for Dr. John McLevey's Networks Lab, University of Waterloo, 2016.
# Permissive free software license - BSD/MIT.
import unittest
import os
import re
import numpy as np
import gitnet
import subprocess as sub


class TestGetLog(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        sub.call(["cp", "-R", "repo_one.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)
        self.my_log.describe()

    # Basic test in default mode.
    def test_basic(self):
        self.assertEqual(len(self.my_log), 3)
        self.assertEqual(type(self.my_log), gitnet.CommitLog)
        self.assertEqual(self.my_log.collection["fc3527c"]["hash"], "fc3527c0eb2e8ee314b551893c88889ad8647c1d")
        self.assertEqual(self.my_log.collection["fc3527c"]["author"], "Alice")
        self.assertEqual(self.my_log.collection["fc3527c"]["email"], "alice@gmail.com")
        self.assertEqual(self.my_log.collection["44b4c72"]["summary"], "3 files changed, 129 insertions(+)")
        self.assertEqual(self.my_log.collection["44b4c72"]["fedits"], int(np.floor(np.pi)))  # xkcd 1275
        self.assertEqual(self.my_log.collection["44b4c72"]["inserts"], 129)
        parse_problems = False
        for record in self.my_log.collection:
            for rkey in self.my_log.collection[record]:
                if rkey == "errors":
                    parse_problems = True
        self.assertEqual(parse_problems, False)

    def test_filter(self):
        self.assertEqual(len(self.my_log.filter("email", "equals", "alice@gmail.com")), 2)
        self.assertEqual(len(self.my_log.filter("email", "equals", "alice@gmail.com", negate=True)), 1)
        self.assertEqual(len(self.my_log.filter("email", "has", "alice")), 2)
        self.assertEqual(len(self.my_log.filter("date", "since", "Fri May 6 14:50:22 2016 -0400")), 2)
        self.assertEqual(len(self.my_log.filter("date", "sincex", "Fri May 6 14:50:22 2016 -0400")), 1)
        self.assertEqual(len(self.my_log.filter("date", "before", "Fri May 6 14:50:22 2016 -0400")), 2)
        self.assertEqual(len(self.my_log.filter("date", "beforex", "Fri May 6 14:50:22 2016 -0400")), 1)
        self.assertEqual(len(self.my_log.filter("email", "has", "[ab][lo][ib]c?e?@gmail.com")), 3)
        self.assertEqual(len(self.my_log.filter("changes", "has", ".txt")), 1)
        self.assertEqual(len(self.my_log.filter("fedits", ">", 1)), 1)
        self.assertEqual(len(self.my_log.filter("fedits", "<", 1)), 0)
        self.assertEqual(len(self.my_log.filter("fedits", "<=", 1)), 2)
        self.assertEqual(len(self.my_log.filter("email", "equals", "@gmail", helper=lambda x, y: y in x)), 3)

    def test_vector(self):
        self.assertEqual(sorted(self.my_log.vector("email")), ["alice@gmail.com", "alice@gmail.com", "bob@gmail.com"])
        self.assertEqual(sorted(self.my_log.vector("fedits")), [1, 1, 3])
        self.assertEqual(sorted(self.my_log.vector("inserts")), [1, 5, 129])
        self.assertEqual(sorted(self.my_log.vector("deletes")), [])
        self.assertEqual(len(self.my_log.collection["44b4c72"]["files"]), 3)

    def test_ignore(self):
        self.assertEqual(len(self.my_log.ignore("\w\w\w\w.txt")["44b4c72"]["files"]), 0)
        self.assertEqual(len(self.my_log.ignore("\w\w\w\w_")["44b4c72"]["files"]), 1)
        self.assertEqual(len(self.my_log.ignore("\.md$")["fc3527c"]["files"]), 0)

    def tearDown(self):
        sub.call(["rm", "-rf", ".git"])


class TestBigGit(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        sub.call(["cp", "-R", "repo_nx.git", ".git"])
        self.good_path = os.getcwd()
        self.nx_log = gitnet.get_log(self.good_path)

    def test_get_big(self):
        self.assertEqual(len(self.nx_log), 4881)
        self.assertEqual(len(self.nx_log.vector("errors")), 0)

    def test_big_tsv(self):
        tabs = self.nx_log.tsv()
        for hsh in self.nx_log:
            self.assertTrue(hsh in tabs)
        self.nx_log.tsv(fname="nx_test.tsv")
        f = open("nx_test.tsv", "r")
        nx_lines = f.readlines()
        self.assertEqual(len(nx_lines), 4882)
        self.assertEqual(re.sub('[\s+]', '', nx_lines[0]), "hashauthoremaildatemodemergesummaryfedits"
                                                           "insertsdeletesmessagefileschanges")
        f.close()
        sub.call(["rm", "nx_test.tsv"])

    def tearDown(self):
        sub.call(["rm", "-rf", ".git"])


class TestGetError(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        # sub.call(["cp","-R","repo_zero.git",".git"])
        sub.call(["git", "init"])
        self.bad_path = os.getcwd()

    # Test that a RepositoryError is raised when accessing a repository with no commits.
    def test_no_commits(self):
        with self.assertRaises(gitnet.RepositoryError):
            print(self.bad_path)
            gitnet.get_log(self.bad_path)

    # Test that an InputError is raised when calling get_log with an invalid input mode.
    def test_invalid_mode(self):
        with self.assertRaises(gitnet.InputError):
            gitnet.get_log(self.bad_path, mode="hoolagin")

    # Test that a Repository Error is raised when accessing a directory that is not a git repo.
    def test_no_repo(self):
        with self.assertRaises(gitnet.RepositoryError):
            gitnet.get_log("/")

    def tearDown(self):
        sub.call(["rm", "-rf", ".git"])

if __name__ == '__main__':
    unittest.main(buffer=True)
