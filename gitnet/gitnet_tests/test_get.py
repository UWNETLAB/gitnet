import unittest
import os
import bash as sh
import gitnet

cur_dir = os.getcwd()
if input("Currently working in {}."
         " .git files in this directory will be destroyed."
         " Continue? [y/n]".format(cur_dir)) != "y":
    print("Quitting.")
    exit()

class TestGetLog(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        sh.bash("cp -R repo_one.git .git")
        self.good_path = os.getcwd()

    # Basic test in default mode.
    def test_basic(self):
        my_log = gitnet.get_log(self.good_path)
        self.assertEqual(len(my_log),3)
        self.assertEqual(type(my_log),gitnet.CommitLog)
        self.assertEqual(my_log.collection["fc3527c"]["HA"],"fc3527c0eb2e8ee314b551893c88889ad8647c1d")
        self.assertEqual(my_log.collection["fc3527c"]["AU"],"Alice")
        self.assertEqual(my_log.collection["fc3527c"]["AE"],"alice@gmail.com")
        self.assertEqual(my_log.collection["44b4c72"]["SU"], "3 files changed, 129 insertions(+)")
        parse_problems = False
        for record in my_log.collection:
            for rkey in my_log.collection[record]:
                if rkey == "ER":
                    parse_problems = True
        self.assertEqual(parse_problems, False)

    def tearDown(self):
        sh.bash("rm -rf .git")

class TestGetError(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        sh.bash("cp -R repo_zero.git .git")
        self.bad_path = os.getcwd()

    # Test that a RepositoryError is raised when accessing a repository with no commits.
    def test_no_commits(self):
        with self.assertRaises(gitnet.RepositoryError):
            gitnet.get_log(self.bad_path)

    # Test that an InputError is raised when calling get_log with an invalid input mode.
    def test_invalid_mode(self):
        with self.assertRaises(gitnet.InputError):
            gitnet.get_log(self.bad_path,mode = "hoolagin")

    # Test that a Repository Error is raised when accessing a directory that is not a git repo.
    def test_no_repo(self):
        with self.assertRaises(gitnet.RepositoryError):
            gitnet.get_log("/")

    def tearDown(self):
        sh.bash("rm -rf .git")

if __name__ == '__main__':
    unittest.main()
