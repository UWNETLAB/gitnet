import unittest
import gitnet
import bash as sh
import os


cur_dir = os.getcwd()
if input("Currently working in {}."
         " .git files in this directory will be destroyed."
         " Continue? [y/n]".format(cur_dir)) != "y":
    print("Quitting.")
    exit()


class TestMultiGraph(unittest.TestCase):
    def setup(self):
        # Set up Repo One
        sh.bash("cp -R repo_one.git .git")
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

    def test_node_merge(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
