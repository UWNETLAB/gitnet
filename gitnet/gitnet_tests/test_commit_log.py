import gitnet
import unittest
import subprocess as sub
import os
from unittest.mock import patch
from io import StringIO




class GetTagsTests(unittest.TestCase):

    def test_basic(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        path = os.getcwd()
        my_log = gitnet.get_log(path)

        tags = my_log.get_tags()

        self.assertListEqual(tags, ["hash", "author", "email", "date", "mode", "merge", "summary",
                                    "fedits", "inserts", "deletes", "message", "files", "changes"])

        # Delete temporary .git file
        sub.call(["rm","-rf",".git"])


class DescribeTests(unittest.TestCase):
    def setUp(self):
        # Set up small network
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        path = os.getcwd()
        self.my_log = gitnet.get_log(path)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            ret = self.my_log.describe()
            self.assertIsNone(ret)
        self.output = fake_out.getvalue()

    def test_basic(self):
        """Is there something being printed to the screen?"""
        output = self.output
        self.assertNotEqual(output, "")

    def test_default(self):
        """Does the default method print the proper information?"""
        output = self.output

    def test_not_default(self):
        """ Does a non-default method print the proper information?
            Note: At this point, default is the only setting so they end up being the same."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.my_log.describe(mode="not default")
            self.assertIsNotNone(fake_out)

    def test_exclude(self):
        pass

    def test_filters(self):
        pass

    def test_mult_commits(self):
        """Are multiple commit records by the same author handled correctly?"""
        pass

    def test_bad_email(self):
        """Are badly formated email addresses disregarded?"""
        pass

    def test_changes(self):
        """Are changes to files such as merge and delete displayed?"""
        pass

    def tearDown(self):
        # Delete temporary .git file
        sub.call(["rm","-rf",".git"])


class IgnoreTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class NetworkTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(buffer=True)