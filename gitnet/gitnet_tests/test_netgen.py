import unittest
import os
import bash as sh
import gitnet


class TestEdgeGeneratorSmall(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        sh.bash("cp -R repo_one.git .git")
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

    # Small time edge generation.
    def test_edge_gen(self):
        edges = sorted([("Alice","basic_logs.txt", {}),
                     ("Alice","raw_logs.txt", {}),
                     ("Alice","stat_logs.txt", {}),
                     ("Bob","readme.md", {}),
                     ("Alice","readme.md", {})])
        self.assertEqual(edges,sorted(self.my_log.generate_edges("author","files")))

    def test_edge_attr(self):
        hashes = [e[2]["hash"] for e in self.my_log.generate_edges("author","files",edge_attributes="hash")]
        manual = ["44b4c727133c69cffafc74bb65fd6f8639bc4287",
                  "51ba020a3fdc56d74d88306e507dd4e2d2db3543",
                  "fc3527c0eb2e8ee314b551893c88889ad8647c1d"]
        self.assertEqual(set(hashes),set(manual))

    def test_edge_weight(self):
        weights = [e[2]["weight"] for e in self.my_log.generate_edges("author","files", helper=gitnet.helpers.changes_edge)]
        manual = [33,45,51,1,5]
        self.assertEqual(set(weights),set(manual))

    def test_edge_attr_dict(self):
        edges = self.my_log.generate_edges("author","files", helper=gitnet.helpers.changes_edge,
                                           edge_attributes=["hash","date"])
        attr_dict = [e[2] for e in edges if e[2]["hash"] == "51ba020a3fdc56d74d88306e507dd4e2d2db3543"][0]
        manual_dict = {"weight":1,"hash":"51ba020a3fdc56d74d88306e507dd4e2d2db3543","date":"Fri May 6 14:50:22 2016 -0400"}
        print("Attr Dict:",attr_dict)
        print("Manual Dict:",manual_dict)
        self.assertEqual(attr_dict,manual_dict)

    def tearDown(self):
        sh.bash("rm -rf .git")


if __name__ == '__main__':
    unittest.main()