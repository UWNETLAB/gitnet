import unittest
import os
import warnings
import subprocess as sub
import gitnet


class TestEdgeGeneratorSmall(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        sub.call(["cp","-R","repo_one.git",".git"])
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
        self.assertEqual(attr_dict,manual_dict)

    def tearDown(self):
        sub.call(["rm","-rf",".git"])


class TestNodeGeneratorSmall(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        sub.call(["cp","-R","repo_one.git",".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

    # Small time node generation.
    def test_node_gen(self):
        nodes = [n[0] for n in self.my_log.generate_nodes("author","files")]
        files = ["basic_logs.txt","raw_logs.txt","stat_logs.txt","readme.md"]
        authors = ["Alice", "Bob"]
        for f in files:
            self.assertIn(f,nodes)
        for a in authors:
            self.assertIn(a,nodes)
        self.assertEqual(set(nodes),set(files).union(set(authors)))

    # An exhaustive test of node attributes for a small number of nodes.
    def test_node_attr(self):
        nodes = self.my_log.generate_nodes("author","files",
                                           keep_atom1=["email"],keep_vector1=["date","fedits"],
                                           keep_vector2=["author","date"])
        node_dict = {}
        for n in nodes:
            node_dict[n[0]] = n[1]
            for key in node_dict[n[0]]:
                if type(node_dict[n[0]][key]) is list:
                    node_dict[n[0]][key] = set(node_dict[n[0]][key])
        self.assertEqual(node_dict["Alice"],
                    {"email":"alice@gmail.com",
                     "date":{"Fri May 6 15:41:25 2016 -0400","Fri May 6 14:41:25 2016 -0400"},
                     "fedits":{3,1},
                     "type":"author",
                     "id":"Alice",
                     "records":{"44b4c72","fc3527c"}})
        self.assertEqual(node_dict["Bob"],
                    {"email":"bob@gmail.com",
                     "date":{"Fri May 6 14:50:22 2016 -0400"},
                     "fedits":{1},
                     "type":"author",
                     "id":"Bob",
                     "records":{"51ba020"}})
        self.assertEqual(node_dict["readme.md"],
                    {"author":{"Alice","Bob"},
                     "date":{"Fri May 6 14:50:22 2016 -0400","Fri May 6 14:41:25 2016 -0400"},
                     "type":"files",
                     "id":"readme.md",
                     "records":{"51ba020","fc3527c"}})
        self.assertEqual(node_dict["basic_logs.txt"],
                    {"author":{"Alice"},
                     "date":{"Fri May 6 15:41:25 2016 -0400"},
                     "type":"files",
                     "id":"basic_logs.txt",
                     "records":{"44b4c72"}})
        self.assertEqual(node_dict["stat_logs.txt"],
                    {"author":{"Alice"},
                     "date":{"Fri May 6 15:41:25 2016 -0400"},
                     "type":"files",
                     "id":"stat_logs.txt",
                     "records":{"44b4c72"}})
        self.assertEqual(node_dict["raw_logs.txt"],
                    {"author":{"Alice"},
                     "date":{"Fri May 6 15:41:25 2016 -0400"},
                     "type":"files",
                     "id":"raw_logs.txt",
                     "records":{"44b4c72"}})

    def tearDown(self):
        sub.call(["rm","-rf",".git"])

class TestNetworkGeneratorSmall(unittest.TestCase):

    def setUp(self):
        # Set up Repo One
        sub.call(["cp","-R","repo_one.git",".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

    def test_tag_warning(self):
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            net = self.my_log.generate_network("author", "file")
            # Check Warning occurred
            self.assertEqual(len(w), 1)
            self.assertIn("Dictionary of node attributes is empty. Check that mode1 and mode2 names are valid tags.",
                          str(w[-1].message))

    def test_hash_author(self):
        net = self.my_log.generate_network("hash","author")
        self.assertEqual(net.number_of_nodes(),5)
        self.assertEqual(net.number_of_edges(),3)

    def test_file_author(self):
        net = self.my_log.generate_network("files","author")
        self.assertEqual(net.number_of_nodes(),6)
        self.assertEqual(net.number_of_edges(),5)

    def test_author_file(self):
        net = self.my_log.generate_network("author","files",
                                           mode1_atom_attrs=["email"],
                                           mode1_vector_attrs=["fedits"],
                                           mode2_atom_attrs=[],
                                           mode2_vector_attrs=["date"],
                                           edge_helper=gitnet.changes_edge,
                                           edge_attributes=["hash"])
        self.assertEqual(net.number_of_nodes(),6)
        self.assertEqual(net.number_of_edges(),5)
        net2 = gitnet.MultiGraphPlus()
        net2.add_node("Alice",email="alice@gmail.com",fedits=[3,1],
                      records=["44b4c72","fc3527c"],type="author",id="Alice")
        net2.add_node("Bob",email="bob@gmail.com",fedits=[1],
                      records=["51ba020"],type="author",id="Bob")
        net2.add_node("basic_logs.txt",date=["Fri May 6 15:41:25 2016 -0400"],
                      records=["44b4c72"],id="basic_logs.txt",type="files")
        net2.add_node("stat_logs.txt",date=["Fri May 6 15:41:25 2016 -0400"],
                      records=["44b4c72"],id="stat_logs.txt",type="files")
        net2.add_node("raw_logs.txt",date=["Fri May 6 15:41:25 2016 -0400"],
                      records=["44b4c72"],id="raw_logs.txt",type="files")
        net2.add_node("readme.md",date=["Fri May 6 14:50:22 2016 -0400","Fri May 6 14:41:25 2016 -0400"],
                      records=["51ba020","fc3527c"],id="readme.md",type="files")
        net2.add_edge("Alice","basic_logs.txt",weight=33,hash="44b4c727133c69cffafc74bb65fd6f8639bc4287")
        net2.add_edge("Alice","raw_logs.txt",weight=45,hash="44b4c727133c69cffafc74bb65fd6f8639bc4287")
        net2.add_edge("Alice","stat_logs.txt",weight=51,hash="44b4c727133c69cffafc74bb65fd6f8639bc4287")
        net2.add_edge("Alice","readme.md",weight=5,hash="fc3527c0eb2e8ee314b551893c88889ad8647c1d")
        net2.add_edge("Bob","readme.md",weight=1,hash="51ba020a3fdc56d74d88306e507dd4e2d2db3543")
        for n in net.nodes(data=True):
            for attr in n[1]:
                if type(n[1][attr]) is list:
                    n[1][attr] = set(n[1][attr])
        for n in net2.nodes(data=True):
            for attr in n[1]:
                if type(n[1][attr]) is list:
                    n[1][attr] = set(n[1][attr])
        for n in net.nodes(data=True):
            self.assertEqual(n[1],net2.node[n[0]])
        self.assertEqual(len(net),len(net2))

    def tearDown(self):
        sub.call(["rm","-rf",".git"])

if __name__ == '__main__':
    unittest.main()