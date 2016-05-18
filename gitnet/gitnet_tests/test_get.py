import unittest
import os
import bash as sh
import gitnet

class TestGetLog(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        sh.bash("cp -R repo_one.git .git")
        self.git_path = os.getcwd()

    # Basic test
    def basic_test(self):
        gitnet.get_log(self.git_path)
        assert True

    # Tests whether get_log.py successful retrieves commits from a Git repository in "basic" mode.
    def test_retrieve_basic_commits(self):
        pass

    # Tests whether get_log.py successful retrieves commits from a Git repository in "raw" mode.
    def test_retrieve_raw_commits(self):
        pass

    # Tests whether get_log.py successful retrieves commits from a Git repository in "stat" mode.
    def test_retrieve_stat_commits(self):
        pass

    def tearDown(self):
        sh.bash("rm -r .git")

class RetrievalFailure(unittest.TestCase):
    def setUp(self):
        pass

    # Tests whether get_log.py raises the appropriate error when accessing an inactive Git repository.
    def test_no_commits_failure(self):
        pass

    # Tests whether get_log.py raises the appropriate error when passed an invalid retrieval mode.
    #def test_bad_mode_error(self):
    #        with self.assertRaises(InputError):
    #            gitnet.retrieve_commits(self.test_repo_dir, mode="hoolagin")

    ## Tests whether get_log.py raises the appropriate error when accessing a directory that's not a Git repository.
    #def test_not_repo(self):
    #    with self.assertRaises(RepositoryError):
    #        gitnet.retrieve_commits("/")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
