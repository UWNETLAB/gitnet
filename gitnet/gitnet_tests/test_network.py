# Written by Jillain Anderson, Joel Becker, and Steve McColl for Dr. John McLevey's Networks Lab, University of Waterloo, 2016.
# Permissive free software license - BSD/MIT.
import unittest
from unittest.mock import patch
import gitnet
from gitnet import multigraph
from gitnet.exceptions import MergeError
from gitnet.exceptions import GraphStatsError
import os
import networkx as nx
import subprocess as sub
from io import StringIO
import warnings


class GraphMLTests(unittest.TestCase):
    def setUp(self):
        """Setup to occur before each method executes"""
        self.mg = multigraph.MultiGraphPlus()
        self.mg.add_node('Alice', attr_dict={'id': 'a01',
                                             'type': 'author',
                                             'email': 'alice@gmail.com',
                                             'records': ['hash1', 'hash2']})
        self.mg.add_node('Bobby', attr_dict={'id': 'a02',
                                             'type': 'author',
                                             'email': 'bob@gmail.com',
                                             'records': ['hash3', 'hash4']})
        self.mg.add_node('file01', attr_dict={'id': 'f01',
                                              'type': 'file',
                                              'records': ['hash1', 'hash3']})
        self.mg.add_node('file02', attr_dict={'id': 'f02',
                                              'type': 'file',
                                              'records': ['hash2']})
        self.mg.add_node('file03', attr_dict={'id': 'f03',
                                              'type': 'file',
                                              'records': ['hash4']})

        self.mg.add_edge('Alice', 'file01', key='e01', sha='hash1', changed_lines=[1, 2, 3])
        self.mg.add_edge('Alice', 'file02', key='e02', sha='hash2', changed_lines=[1, 2, 3])
        self.mg.add_edge('Bobby', 'file01', key='e03', sha='hash3', changed_lines=[2, 4, 5])
        self.mg.add_edge('Bobby', 'file03', key='e04', sha='hash4', changed_lines=[1, 2, 3])

        self.made_gml = False
        try:
            os.mkdir('temp')
            self.path = os.getcwd() + '/temp/ABgml.txt'
            self.graphml = self.mg.write_graphml(self.path)
        finally:
            self.made_gml = True

    def test_basic_res(self):
        """Was basic functionality of the method achieved?"""
        # Check that the method doesn't return a value
        self.assertIsNone(self.mg.write_graphml(self.path))
        # Check that a file exists where expected
        self.assertTrue(os.path.exists(self.path))

    def test_rev(self):
        """Test if taking turning the graphml back into networkx yields the expected edges and nodes"""
        rev = nx.read_graphml(self.path)
        self.assertSetEqual({'Alice', 'Bobby', 'file01', 'file02', 'file02', 'file03'}, set(rev.nodes()))
        self.assertSetEqual({'file01', 'file02'}, set(rev.edge['Alice']))
        self.assertSetEqual({'file01', 'file03'}, set(rev.edge['Bobby']))
        self.assertSetEqual({'Alice', 'Bobby'}, set(rev.edge['file01']))
        self.assertSetEqual({'Alice'}, set(rev.edge['file02']))
        self.assertSetEqual({'Bobby'}, set(rev.edge['file03']))

    def test_rev_node_attr(self):
        """Are node attr preserved when we convert the graphml back to a network?"""
        rev = nx.read_graphml(self.path)
        mg = self.mg
        # Check that node attributes still exist
        for n in mg.nodes():
            self.assertIn('id', rev.node[n])
            self.assertIn('type', rev.node[n])
            self.assertIn('records', rev.node[n])
            self.assertIsInstance(rev.node[n]['records'], str)
            if rev.node[n]['type'] == 'author':
                self.assertIn('email', rev.node[n])

        # Check that node attributes haven't been added
        for n in rev.nodes():
            self.assertEqual(len(mg.node[n]), len(rev.node[n]))

        # Check that node attribute values are the same
        for n in rev.nodes():
            for k in rev.node[n]:
                if not isinstance(mg.node[n][k], list):
                    self.assertEqual(mg.node[n][k], rev.node[n][k])
                else:
                    self.assertEqual(";".join(mg.node[n][k]), rev.node[n][k])

    def test_rev_edge_attr(self):
        """Are edge attr preserved when we convert the graphml back to a network?"""
        rev = nx.read_graphml(self.path)
        mg = self.mg
        # Check that edge attributes still exist
        for n1, n2, data in self.mg.edges(data=True):
            self.assertIn('sha', rev.edge[n1][n2])

        # Check that edge attributes are correct (atomic and vector)
        for n1, n2, data in mg.edges(data=True):
            for k in data:
                if not isinstance(data[k], list):
                    self.assertEqual(data[k], rev.edge[n1][n2][k])
                else:
                    self.assertEqual(gitnet.helpers.list_to_scd(data[k]), rev.edge[n1][n2][k])

    def test_warnings(self):
        """Are appropriate warnings being raised iff they should be?"""
        mg = self.mg

        # Warning occurs when vector edge and node attributes are provided
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            mg.write_graphml(self.path)
            # Check Warning occurred
            self.assertEqual(len(w), 1)
            self.assertIn("'n:records'", str(w[-1].message))
            self.assertIn("'e:changed_lines'", str(w[-1].message))

        # Warning occurs when vector edge attributes are provided
        mg_edge = multigraph.MultiGraphPlus()
        mg_edge.add_edge("A", "B", changed_lines=[1, 2, 3])
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            mg_edge.write_graphml(self.path)
            # Check Warning occurred
            self.assertEqual(len(w), 1)
            self.assertIn("e:changed_lines'", str(w[-1].message))

        # Warning includes correct list of vector attributes
        mg.add_node("Charles", attr_dict={'id': 'a03',
                                          'email': 'charles@gmail.com',
                                          'affiliations': ['Uwaterloo', 'Netlab']})
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            mg.write_graphml(self.path)
            # Check Warning occurred properly
            self.assertEqual(len(w), 1)
            self.assertIn("'n:records'", str(w[-1].message))
            self.assertIn("'n:affiliations'", str(w[-1].message))
            self.assertIn("'e:changed_lines'", str(w[-1].message))

        # Warning doesn't occur when no attributes are present
        mg_nowarn = multigraph.MultiGraphPlus()
        mg_nowarn.add_edge('Charlie', 'filea')
        mg_nowarn.add_edge('Charlie', 'fileb')
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            mg_nowarn.write_graphml(self.path)
            # Check Warning didn't occurred
            self.assertEqual(len(w), 0)

        # Warning doesn't occur when only atomic attributes are present
        mg_atomic = multigraph.MultiGraphPlus()
        mg_atomic.add_node('Dawn', attr_dict={'id': 'a04', 'email': 'dawn@yahoo.ca'})
        mg_atomic.add_node('filec', attr_dict={'id': 'f0c'})
        mg_atomic.add_edge('Dawn', 'filec', date='Jan 4')
        with warnings.catch_warnings(record=True) as w:
            # Ensure warnings are being shown
            warnings.simplefilter("always")
            # Trigger Warning
            mg_atomic.write_graphml(self.path)
            # Check Warning didn't occurred
            self.assertEqual(len(w), 0)

    def tearDown(self):
        if self.made_gml:
            os.remove(self.path)
            os.rmdir('temp')


class TnetTests(unittest.TestCase):
    def setUp(self):
        """Setup to occur before each method executes"""
        self.mg = multigraph.MultiGraphPlus()
        self.mg.add_node('Alice', attr_dict={'id': 'a01',
                                             'type': 'author',
                                             'email': 'alice@gmail.com',
                                             'records': ['hash1', 'hash2']})
        self.mg.add_node('Bobby', attr_dict={'id': 'a02',
                                             'type': 'author',
                                             'email': 'bob@gmail.com',
                                             'records': ['hash3', 'hash4']})
        self.mg.add_node('file01', attr_dict={'id': 'f01',
                                              'type': 'file',
                                              'records': ['hash1', 'hash3']})
        self.mg.add_node('file02', attr_dict={'id': 'f02',
                                              'type': 'file',
                                              'records': ['hash2']})
        self.mg.add_node('file03', attr_dict={'id': 'f03',
                                              'type': 'file',
                                              'records': ['hash4']})

        self.mg.add_edge('Alice', 'file01', sha='hash1', weight=1)
        self.mg.add_edge('Alice', 'file02', sha='hash2', weight=1)
        self.mg.add_edge('Bobby', 'file01', sha='hash3', weight=1)
        self.mg.add_edge('Bobby', 'file03', sha='hash4', weight=1)

        self.made_tnet = False
        try:
            os.mkdir('temp')
            self.path = os.getcwd() + '/temp/tnet.txt'
            self.tnet = self.mg.write_tnet(self.path)
        finally:
            self.made_tnet = True

    def test_basic(self):
        """Is basic functionality of the method achieved?"""
        # Check that the method doesn't return a value
        self.assertIsNone(self.mg.write_tnet(self.path))
        # Check that a file exists where expected
        self.assertTrue(os.path.exists(self.path))

    def test_date(self):
        """Is basic functionality achieved when date is given in the edge?"""
        # Add edge with a date
        self.mg.add_edge('Alice', 'file03', date='Thu Feb 4 09:13:45 2016 -0600', weight=1)
        # Check method doesn't return a value
        self.assertIsNone(self.mg.write_tnet(self.path))
        # Check a file exists where expected
        self.assertTrue(os.path.exists(self.path))

    def test_weighted(self):
        # Check method executes and doesn't return a value when weighted = True
        self.assertIsNone(self.mg.write_tnet(self.path, weighted=True))
        # Check a file exists where expected
        self.assertTrue(os.path.exists(self.path))

    def test_None_timestr(self):
        # Check method executes and doesn't return a value when time_string = None
        self.assertIsNone(self.mg.write_tnet(self.path, time_string=None))
        # Check a file exists where expected
        self.assertTrue(os.path.exists(self.path))

    def test_mode_errors(self):
        """Are errors raised when there is an incorrect number of modes or if edges are occuring between modes?"""
        # Create a graph with only 1 mode
        mg = multigraph.MultiGraphPlus()
        mg.add_node('Alice', attr_dict={'id': 'a01',
                                        'type': 'author',
                                        'email': 'alice@gmail.com',
                                        'records': ['hash1']})
        mg.add_node('Bobby', attr_dict={'id': 'a02',
                                        'type': 'author',
                                        'email': 'bob@gmail.com',
                                        'records': ['hash2', 'hash3']})
        # Checking the right error occurs
        with self.assertRaisesRegex(ValueError, "Too few modes of 'type' found in the network. "
                                                "There must be exactly 2 modes."):
            mg.write_tnet(self.path)

        # Adding 2 more modes
        mg.add_node('file01', attr_dict={'id': 'f01',
                                         'type': 'file',
                                         'records': ['hash1', 'hash2']})
        mg.add_node('file02', attr_dict={'id': 'f02',
                                         'type': 'file',
                                         'records': ['hash1']})
        mg.add_node('UWaterloo', attr_dict={'id': 'u01',
                                            'type': 'university',
                                            'records': ['hash3']})

        mg.add_edge('Alice', 'file01', sha='hash1', weight=1)
        mg.add_edge('Alice', 'file02', sha='hash1', weight=1)
        mg.add_edge('Bobby', 'file01', sha='hash2', weight=1)
        mg.add_edge('Bobby', 'UWaterloo', sha='hash2', weight=1)

        # Checking the right error occurs
        with self.assertRaisesRegex(ValueError, "Too many modes of 'type' found in the network or one of the nodes was "
                                                "missing its mode. There must be exactly 2 modes."):
            mg.write_tnet(self.path)

        # Adding an edge between equal modes
        mg.remove_node('UWaterloo')  # Remove to prevent error
        mg.add_edge('Alice', 'Bobby', sha='hash5', weight=1)

        # Checking the right error occurs
        with self.assertRaisesRegex(ValueError, "The nodes '(Alice|Bobby)' and '(Alice|Bobby)' have an edge and the "
                                                "same type. The network must be purely 2-mode."):
            mg.write_tnet(self.path)

    def test_other_errors(self):
        mg = multigraph.MultiGraphPlus()
        mg.add_node('Alice', attr_dict={'id': 'a01',
                                        'type': 'author',
                                        'email': 'alice@gmail.com',
                                        'records': ['hash1']})
        mg.add_node('Bobby', attr_dict={'id': 'a02',
                                        'type': 'author',
                                        'email': 'bob@gmail.com',
                                        'records': ['hash2']})
        mg.add_node('file01', attr_dict={'id': 'f01',
                                         'type': 'file',
                                         'records': ['hash1', 'hash2']})
        mg.add_edge('Alice', 'file01', date='Thu Feb 4 09:13:45 2016 -0600')
        mg.add_edge('Bobby', 'file01', date='Fri Feb 5 09:13:45 2016 -0600')

        # Ensuring a warning is raised when the mode_string isn't an attribute of each node
        with self.assertRaises(ValueError):
            mg.write_tnet(self.path, mode_string="email")

    def tearDown(self):
        if self.made_tnet:
            os.remove(self.path)
            os.rmdir('temp')


class NodeAttrTests(unittest.TestCase):
    def setUp(self):
        self.mg = multigraph.MultiGraphPlus()
        self.mg.add_node('Alice', attr_dict={'id': 'a01',
                                             'email': 'alice@gmail.com',
                                             'type': 'author',
                                             'records': ['hash1']})
        self.mg.add_node('Bobby', attr_dict={'id': 'a02',
                                             'email': 'bobby@gmail.com',
                                             'type': 'author',
                                             'records': ['hash2']})
        self.mg.add_node('file01', attr_dict={'id': 'f01',
                                              'type': 'file',
                                              'records': ['hash1', 'hash2']})
        self.mg.add_node('file02', attr_dict={'id': 'f02',
                                              'type': 'file',
                                              'records': ['hash1']})
        self.mg.add_edge('file01', 'Alice', date='Jan 1')
        self.mg.add_edge('file02', 'Alice', date='Jan 2')
        self.mg.add_edge('file01', 'Bobby', date='Jan 3')

    def test_basic(self):
        # Creating the expected output from the function
        expected_mg = multigraph.MultiGraphPlus()
        expected_mg.add_node('Alice', attr_dict={'id': 'a01',
                                                 'email': 'alice@gmail.com',
                                                 'type': 'author',
                                                 'records': ['hash1'],
                                                 'colour': 'dodgerblue'})
        expected_mg.add_node('Bobby', attr_dict={'id': 'a02',
                                                 'email': 'bobby@gmail.com',
                                                 'type': 'author',
                                                 'records': ['hash2'],
                                                 'colour': 'dodgerblue'})
        expected_mg.add_node('file01', attr_dict={'id': 'f01',
                                                  'type': 'file',
                                                  'records': ['hash1', 'hash2'],
                                                  'colour': 'red'})
        expected_mg.add_node('file02', attr_dict={'id': 'f02',
                                                  'type': 'file',
                                                  'records': ['hash1'],
                                                  'colour': 'red'})
        expected_mg.add_edge('file01', 'Alice', date='Jan 1')
        expected_mg.add_edge('file02', 'Alice', date='Jan 2')
        expected_mg.add_edge('file01', 'Bobby', date='Jan 3')

        # Defining the helper function for node_attributes
        def helper(d):
            colour = 'red'
            if d['type'] == 'author':
                colour = 'dodgerblue'
            return colour

        self.assertIsInstance(self.mg.node_attributes('colour', helper), multigraph.MultiGraphPlus)
        self.assertDictEqual(self.mg.node_attributes('colour', helper).node['Alice'],
                             expected_mg.node['Alice'])
        self.assertDictEqual(self.mg.node_attributes('colour', helper).node['Bobby'],
                             expected_mg.node['Bobby'])
        self.assertDictEqual(self.mg.node_attributes('colour', helper).node['file01'],
                             expected_mg.node['file01'])
        self.assertDictEqual(self.mg.node_attributes('colour', helper).node['file02'],
                             expected_mg.node['file02'])

    def test_attr_there(self):
        expected_mg = multigraph.MultiGraphPlus()
        expected_mg.add_node('Alice', attr_dict={'id': 'a01',
                                                 'email': 'alice@gmail.com',
                                                 'type': 'contributor',
                                                 'records': ['hash1']})
        expected_mg.add_node('Bobby', attr_dict={'id': 'a02',
                                                 'email': 'bobby@gmail.com',
                                                 'type': 'contributor',
                                                 'records': ['hash2']})
        expected_mg.add_node('file01', attr_dict={'id': 'f01',
                                                  'type': 'file',
                                                  'records': ['hash1', 'hash2']})
        expected_mg.add_node('file02', attr_dict={'id': 'f02',
                                                  'type': 'file',
                                                  'records': ['hash1']})
        expected_mg.add_edge('file01', 'Alice', date='Jan 1')
        expected_mg.add_edge('file02', 'Alice', date='Jan 2')
        expected_mg.add_edge('file01', 'Bobby', date='Jan 3')

        # Defining the helper function for node_attributes
        def helper(d):
            node_type = 'file'
            if d['type'] == 'author':
                node_type = 'contributor'
            return node_type

        self.assertIsInstance(self.mg.node_attributes('type', helper), multigraph.MultiGraphPlus)
        self.assertDictEqual(self.mg.node_attributes('type', helper).node['Alice'],
                             expected_mg.node['Alice'])
        self.assertDictEqual(self.mg.node_attributes('type', helper).node['Bobby'],
                             expected_mg.node['Bobby'])
        self.assertDictEqual(self.mg.node_attributes('type', helper).node['file01'],
                             expected_mg.node['file01'])
        self.assertDictEqual(self.mg.node_attributes('type', helper).node['file02'],
                             expected_mg.node['file02'])


class QuickPlotTests(unittest.TestCase):
    """Tests for basic functionality of the quickplot() method"""
    def setUp(self):
        self.mg = multigraph.MultiGraphPlus()

        self.mg.add_node('Alice', attr_dict={'id': 'a01',
                                             'email': 'alice@gmail.com',
                                             'type': 'author',
                                             'records': ['hash1']})
        self.mg.add_node('Bobby', attr_dict={'id': 'a02',
                                             'email': 'bobby@gmail.com',
                                             'type': 'author',
                                             'records': ['hash2']})
        self.mg.add_node('file01', attr_dict={'id': 'f01',
                                              'type': 'file',
                                              'records': ['hash1', 'hash2']})
        self.mg.add_node('file02', attr_dict={'id': 'f02',
                                              'type': 'file',
                                              'records': ['hash1']})
        self.mg.add_edge('file01', 'Alice', date='Jan 1')
        self.mg.add_edge('file02', 'Alice', date='Jan 2')
        self.mg.add_edge('file01', 'Bobby', date='Jan 3')

        # Creating a spot for the image
        self.made_qp = False
        try:
            os.mkdir('temp')
            self.path = os.getcwd() + '/temp/quickplot.png'
            self.qp = self.mg.quickplot(self.path, layout='spring')
        finally:
            self.made_qp = True

    def test_basic(self):
        """Is basic functionality achieved?"""
        # Check that the method doesn't return a value
        self.assertIsNone(self.mg.quickplot(self.path, layout="spring"))
        # Check that a file exists where expected
        self.assertTrue(os.path.exists(self.path))

    def test_layouts(self):
        """Do all of the layouts run?"""
        self.assertIsNone(self.mg.quickplot(self.path, layout="spring"))
        self.assertIsNone(self.mg.quickplot(self.path, layout="circular"))
        self.assertIsNone(self.mg.quickplot(self.path, layout="shell"))
        self.assertIsNone(self.mg.quickplot(self.path, layout="spectral"))
        self.assertIsNone(self.mg.quickplot(self.path, layout="random"))

        # Graphviz Layouts
        # self.assertIsNone(self.mg.quickplot(self.path, layout="dot"))
        # self.assertIsNone(self.mg.quickplot(self.path, layout="neato"))
        # self.assertIsNone(self.mg.quickplot(self.path, layout="fdp"))
        # self.assertIsNone(self.mg.quickplot(self.path, layout="circo"))

    def test_colour(self):
        colour_mg = multigraph.MultiGraphPlus()

        colour_mg.add_node('Alice', attr_dict={'id': 'a01',
                                               'type': 'author',
                                               'colour': 'blue'})
        colour_mg.add_node('Bobby', attr_dict={'id': 'a02',
                                               'type': 'author',
                                               'colour': 'blue'})
        colour_mg.add_node('file01', attr_dict={'id': 'f01',
                                                'type': 'file',
                                                'colour': 'red'})
        colour_mg.add_edge('file01', 'Alice', date='Jan 2')
        colour_mg.add_edge('file01', 'Bobby', date='Jan 3')
        # Checking basic functionality is achieved when colour is an attribute
        self.assertIsNone(colour_mg.quickplot(self.path, layout="spring"))

    def test_color(self):
        color_mg = multigraph.MultiGraphPlus()

        color_mg.add_node('Alice', attr_dict={'id': 'a01',
                                              'type': 'author',
                                              'color': 'blue'})
        color_mg.add_node('Bobby', attr_dict={'id': 'a02',
                                              'type': 'author',
                                              'color': 'blue'})
        color_mg.add_node('file01', attr_dict={'id': 'f01',
                                               'type': 'file',
                                               'color': 'red'})
        color_mg.add_edge('file01', 'Alice', date='Jan 2')
        color_mg.add_edge('file01', 'Bobby', date='Jan 3')
        # Checking basic functionality is achieved when color is an attribute
        self.assertIsNone(color_mg.quickplot(self.path, layout="spring"))

    def tearDown(self):
        if self.made_qp:
            os.remove(self.path)
            os.rmdir('temp')


class DescribeTest(unittest.TestCase):
    """Testing of the describe method in the MultiGraphPlus class."""
    # A small network containing 11 nodes and 11 edges, 4 authors and 7 files.
    # Has a rough density of around 0.39.

    def setUp(self):
        # Prepare small network repo for testing.
        sub.call(["cp","-R","small_network_repo.git",".git"])
        self.path = os.getcwd()
        self.mylogs = gitnet.get_log(self.path)
        self.mgraph = self.mylogs.generate_network('author', 'files')

    def test_type_check(self):
        self.assertIsInstance(self.mgraph, multigraph.MultiGraphPlus)

    def test_stats(self):
        description = self.mgraph.describe()
        self.assertIn("7 nodes are of the type 'files'", description)
        self.assertIn("4 nodes are of the type 'author'", description)
        self.assertIn("11 edges", description)
        self.assertIn("Density: 0.39285", description)

    def test_extra(self):
        """Are results as expected when extra is set to True?"""
        description = self.mgraph.describe(extra=True)
        self.assertIn("7 nodes are of the type 'files'", description)
        self.assertIn("4 nodes are of the type 'author'", description)
        self.assertIn("11 edges", description)
        self.assertIn("Density: 0.39285", description)
        self.assertIn("Transitivity: ", description)
        self.assertIn("Mean Degree Centrality for 'files':", description)
        self.assertIn("Mean Degree Centrality for 'author':", description)
        self.assertIn("Mean Betweenness Centrality for 'files'", description)
        self.assertIn("Mean Betweenness Centrality for 'author'", description)

    def tearDown(self):
        sub.call(["rm","-rf",".git"])


class NodeMergeTest(unittest.TestCase):
    """Tests for the node_merge() method within multigraph.py"""

    def setUp(self):
        self.mg = multigraph.MultiGraphPlus()
        self.mg.add_node('Alice', attr_dict={'id': 'a01',
                                             'email': 'alice@gmail.com',
                                             'phone': '1(888)123-4567',
                                             'type': 'author',
                                             'records': ['hash1', 'hash2'],
                                             'affiliations': ['Uwaterloo', 'Networks Lab']})
        self.mg.add_node('Alice Smith', attr_dict={'id': 'a02',
                                                   'email': 'alice@gmail.ca',
                                                   'type': 'author',
                                                   'colour': 'blue',
                                                   'records': ['hash3', 'hash4'],
                                                   'languages': ['Python', 'C']})
        self.mg.add_node('file02', attr_dict={'id': 'f02',
                                              'type': 'file'})
        self.mg.add_edge('file01', 'Alice', date='Jan 1', style='dotted')
        self.mg.add_edge('Alice Smith', 'file02', date='Jan 2', type='commit')
        self.mg_merged = self.mg.node_merge('Alice Smith', 'Alice', show_warning=False)

    def test_basic_res(self):
        """Ensures the results of the method are appropriate"""
        mg_merged = self.mg_merged
        # Checking Return Value
        self.assertIsInstance(mg_merged, multigraph.MultiGraphPlus)
        # Checking Nodes
        self.assertEqual(self.mg.number_of_nodes(), 4)  # Checking before
        self.assertEqual(mg_merged.number_of_nodes(), 3)
        self.assertEqual(set(mg_merged.nodes()), {'Alice Smith', 'file01', 'file02'})
        self.assertNotIn('Alice', mg_merged.nodes())
        # Checking Edges
        self.assertEqual(self.mg.number_of_edges(), 2)  # Checking before
        self.assertEqual(mg_merged.number_of_edges(), 2)
        self.assertIn('file01', mg_merged.edge['Alice Smith'])
        self.assertIn('file02', mg_merged.edge['Alice Smith'])
        self.assertIn('Alice Smith', mg_merged.edge['file01'])
        self.assertIn('Alice Smith', mg_merged.edge['file02'])
        self.assertNotIn('Alice', mg_merged.edge['file01'])
        self.assertNotIn('Alice', mg_merged.edge['file02'])

    def test_list_attr(self):
        """Are list attributes combined by node_merge?"""
        mg_merged = self.mg_merged
        self.assertIsInstance(mg_merged, multigraph.MultiGraphPlus)
        self.assertEqual(len(mg_merged.node['Alice Smith']['records']), 4)
        self.assertSetEqual(set(mg_merged.node['Alice Smith']['records']), {'hash1', 'hash2', 'hash3', 'hash4'})

    def test_ncon_attr(self):
        """Are the nodes' non-conflicting attributes present in the final node?"""
        mg_merged = self.mg_merged
        self.assertEqual(len(mg_merged.node['Alice Smith']), 8)
        self.assertEqual(mg_merged.node['Alice Smith']['phone'], '1(888)123-4567')
        self.assertSetEqual(set(mg_merged.node['Alice Smith']['affiliations']), {'Uwaterloo', 'Networks Lab'})
        self.assertEqual(mg_merged.node['Alice Smith']['colour'], 'blue')
        self.assertSetEqual(set(mg_merged.node['Alice Smith']['languages']), {'Python', 'C'})

    def test_conf_attr(self):
        """When conflicting atomic attributes are present, are node1's retained?"""
        mg = self.mg
        mg_merged = self.mg_merged
        # Checking that all atomic attributes in node1 are retained
        for a in mg.node['Alice Smith']:
            if not isinstance(mg.node['Alice Smith'][a], list):
                self.assertEqual(mg.node['Alice Smith'][a], mg_merged.node['Alice Smith'][a])
        # Checking conflicting attributes from node2 have been overwritten
        self.assertNotEqual(mg.node['Alice']['id'], mg_merged.node['Alice Smith']['email'])
        self.assertNotEqual(mg.node['Alice']['id'], mg_merged.node['Alice Smith']['id'])

    def test_node_gone(self):
        """Does the method delete node2, and keep node1?"""
        mg = self.mg
        mg_merged = self.mg_merged
        self.assertNotEqual(mg.number_of_nodes(), mg_merged.number_of_nodes())
        self.assertEqual(mg.number_of_nodes()-1, mg_merged.number_of_nodes())
        self.assertEqual(mg_merged.number_of_nodes(), 3)
        with self.assertRaises(KeyError):
           mg_merged.node['Alice']  # Delete node2?
        self.assertIsNotNone(mg_merged.node['Alice Smith'])  # Kept node1?

    def test_edge_attr(self):
        """Does the method retain edge attributes?"""
        mg = self.mg
        mg.add_edge('Alice','file04', date='Jan 19')
        mg_merged = mg.node_merge('Alice Smith', 'Alice')
        node1 = 'Alice Smith'
        node2 = 'Alice'
        # Checking if each edge in the original graph has the same attr as its corresponding edge in the merged graph
        for n1, n2, data in mg.edges(data=True):
            if n1 == node2:
                self.assertDictEqual(mg.edge[n1][n2], mg_merged.edge[node1][n2])
            elif n2 == node2:
                self.assertDictEqual(mg.edge[n1][n2], mg_merged.edge[n1][node1])
            else:
                self.assertDictEqual(mg.edge[n1][n2], mg_merged.edge[n1][n2])
        # Checking an edge explicitly to ensure
        self.assertDictEqual(mg.edge['Alice']['file01'], mg_merged.edge['Alice Smith']['file01'])

    def test_edge_tran(self):
        """Are all of node2's edges transferred to node1?"""
        mg = self.mg
        mg_merged = self.mg_merged
        node1 = 'Alice Smith'
        node2 = 'Alice'
        # Check that node1's edges now include node2's old edges
        self.assertEqual(len(mg_merged.edge[node1]), len(mg.edge[node1])+len(mg.edge[node2]))
        self.assertEqual(len(mg_merged.edge[node1]), 2)
        # Check that the edges to node2 no longer exist
        with self.assertRaises(KeyError):
            mg_merged.edge['Alice']

    def test_mult_edge(self):
        """Are multiple edges handled correctly?
         Ex. A1->B, A2->B. Then merge A1 and A2. """
        mg = self.mg
        mg.add_edge("Alice", "file02", date='Jan 17')
        mg_merged = mg.node_merge('Alice Smith', 'Alice', show_warning=False)
        # Check all edges are retained
        self.assertEqual(len(mg_merged.edges()),3)
        self.assertEqual(len(mg_merged.edge['Alice Smith']), 2)
        self.assertEqual(len(mg.edge['Alice Smith']['file02']), 1)  # Check Before
        self.assertEqual(len(mg_merged.edge['Alice Smith']['file02']), 2)  # Check After
        # Make sure duplicate edges within mg are kept
        mg.add_edge('Alice', 'file02', date='Jan 21')
        mg_merged = mg.node_merge('Alice Smith', 'Alice', show_warning=False)
        self.assertEqual(len(mg_merged.edges()), 4)
        self.assertEqual(len(mg_merged.edge['Alice Smith']), 2)
        self.assertEqual(len(mg.edge['Alice Smith']['file02']), 1)  # Before
        self.assertEqual(len(mg_merged.edge['Alice Smith']['file02']), 3)  # After

    def test_show_warn(self):
        """Does the show_warning parameter act as anticipated?"""
        node1 = 'Alice Smith'
        node2 = 'Alice'
        warn_msg1 = "Note: nodes '{}' and '{}' have the following conflicting atomic attributes: {}. In these cases, " \
                    "'{}' attribute values have been retained, while '{}' values have been ignored. If you would " \
                    "rather retain '{}' attributes, set '{}' to node1 and '{}' to node2.\n"\
                    .format(node1, node2, ['email','id'], node1, node2, node2, node2, node1)
        warn_msg2 = "Note: nodes '{}' and '{}' have the following conflicting atomic attributes: {}. In these cases, " \
                    "'{}' attribute values have been retained, while '{}' values have been ignored. If you would " \
                    "rather retain '{}' attributes, set '{}' to node1 and '{}' to node2.\n" \
                    .format(node1, node2, ['id', 'email'], node1, node2, node2, node2, node1)

        # Checking if the default show_warning parameter prints a message to the screen
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.mg.node_merge(node1, node2)
            self.assertTrue((fake_out.getvalue() == warn_msg1) or (fake_out.getvalue() == warn_msg2))

        # Checking if the explicit show_warning = True prints a message to the screen
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.mg.node_merge(node1, node2)
            self.assertTrue((fake_out.getvalue() == warn_msg1) or (fake_out.getvalue() == warn_msg2))

        # Checking if the false show_warning parameter  doesn't print message to the screen
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.mg.node_merge(node1, node2, show_warning=False)
            self.assertEqual(fake_out.getvalue(), "")

    def test_warn_ovrt(self):
        """Is the overwrite warning(print statement) printed at the right time?"""

        # Merging when no shared attributes -> No output
        mg = self.mg
        mg.add_node('Alice S')
        with patch('sys.stdout', new=StringIO()) as fake_out:
            mg.node_merge("Alice S", "Alice")
            self.assertEqual(fake_out.getvalue(), "")

        # Merging when shared but non-conflicting attributes -> No output
        mg = self.mg
        mg.add_node('Alice S', attr_dict={'email': 'alice@gmail.ca'})
        with patch('sys.stdout', new=StringIO()) as fake_out:
            mg.node_merge("Alice Smith", "Alice S")
            self.assertEqual(fake_out.getvalue(), "")

        # Merging when shared list attributes -> No Output
        mg = self.mg
        mg.add_node('Alice S', attr_dict={'records': ['hash5', 'hash6']})
        with patch('sys.stdout', new=StringIO()) as fake_out:
            mg.node_merge("Alice Smith", "Alice S")
            self.assertEqual(fake_out.getvalue(), "")

        # Merging when conflicting atomic attributes -> Output
        mg = self.mg
        with patch('sys.stdout', new=StringIO()) as fake_out:
            mg_merged = mg.node_merge("Alice Smith", "Alice")
            self.assertNotEqual(fake_out.getvalue(), "")
            self.assertIn("Note: nodes 'Alice Smith' and 'Alice", fake_out.getvalue())

    def test_errors(self):
        """Are errors being raised at the correct times?"""
        mg = self.mg

        # Is there an error when nodes aren't in the graph?
        with self.assertRaises(MergeError):
            mg.node_merge('Bob', 'Alice')
        with self.assertRaises(MergeError):
            mg.node_merge('Alice', 'Bob')
        with self.assertRaises(MergeError):
            mg.node_merge('Bob', 'Bobby')

        # Error raised when trying to merge nodes of different types?
        with self.assertRaises(MergeError):
            mg.node_merge('Alice', 'file02')
        with self.assertRaises(MergeError):
            mg.node_merge('file02', 'Alice')


class CollapseEdgesTest(unittest.TestCase):
    """Tests for the collapse_edges() method within multigraph.py"""
    def setUp(self):
        # A simple graph with weights
        self.mgw = multigraph.MultiGraphPlus()
        self.mgw.add_edge(1, 2, weight=3)
        self.mgw.add_edge(1, 2, weight=2)
        self.mgw.add_edge(2, 3, weight=4)

        # A graph with no weights, but other similar attributes
        self.now = multigraph.MultiGraphPlus()
        self.now.add_edge('Alice', 'file01', type='commit', date='Jan 3', changed_lines=[5, 18, 38, 44])
        self.now.add_edge('file01', 'Alice', type='commit', date='Jan 5', changed_lines=[3, 5, 23, 67])
        self.now.add_edge('file01', 'Bob', type='issue', date='Jan 16', importance='high')

        # A graph whose edges have weights and other different attributes
        self.diff = multigraph.MultiGraphPlus()
        self.diff.add_edge('Charlie', 'file02', weight=2, type='commit', date='Jan 1', changed_lines=[1, 2])
        self.diff.add_edge('Charlie', 'file02', weight=1, type='issue', date='Jan 2', importance='high')
        self.diff.add_edge('Charlie', 'file02', weight=4, type='review', date='Jan 5', status='PASS')
        self.diff.add_edge('Dawn', 'file02', weight=3, type='commit', date='Jan 3', changed_lines=[1, 2, 3])
        self.diff.add_edge('Dawn', 'file02', weight=1, type='issue', date='Jan 12', importance='low')
        self.diff.add_edge('Dawn', 'file02', weight=2, type='issue', date='Jan 23', importance='high')
        self.diff.add_edge('Elise', 'file02', weight=2, type='commit', date='Jan 30', changed_lines=[4, 5])

    def test_simple(self):
        """When sum_weights==False, or isn't provided, are weights calculated by adding number of edges?"""
        # sum_weights is made explicit
        sumwf_explicit = self.mgw.collapse_edges(sum_weights=False)
        self.assertIsInstance(sumwf_explicit, multigraph.MultiGraphPlus)
        self.assertEqual(sumwf_explicit.edge[1][2][0]['weight'], 2)
        self.assertEqual(sumwf_explicit.edge[2][3][0]['weight'], 1)
        self.assertEqual(len(sumwf_explicit.edge[1]), 1)
        self.assertEqual(len(sumwf_explicit.edge[2]), 2)
        self.assertEqual(len(sumwf_explicit.edge[3]), 1)

        # sum_weights is left to the default
        sumwf = self.mgw.collapse_edges()
        self.assertIsInstance(sumwf, multigraph.MultiGraphPlus)
        self.assertEqual(sumwf.edge[1][2][0]['weight'], 2)
        self.assertEqual(sumwf.edge[2][3][0]['weight'], 1)
        self.assertEqual(len(sumwf.edge[1]), 1)
        self.assertEqual(len(sumwf.edge[2]), 2)
        self.assertEqual(len(sumwf.edge[3]), 1)

    def test_simple_sum_weights(self):
        """When sum_weights==True, are weights added?"""
        sumwt = self.mgw.collapse_edges(sum_weights=True)
        self.assertIsInstance(sumwt, multigraph.MultiGraphPlus)
        self.assertEqual(sumwt.edge[1][2][0]['weight'], 5)
        self.assertEqual(sumwt.edge[2][3][0]['weight'], 4)
        self.assertEqual(len(sumwt.edge[1]), 1)
        self.assertEqual(len(sumwt.edge[2]), 2)
        self.assertEqual(len(sumwt.edge[3]), 1)

    def test_no_weight(self):
        """Is the absence of a weight attribute handled correctly? (Default to 1)?"""
        # Summing the weights
        summ = self.now.collapse_edges(sum_weights=True)
        self.assertIsInstance(summ, multigraph.MultiGraphPlus)
        self.assertEqual(summ.edge['Alice']['file01'][0]['weight'], 2)
        self.assertEqual(summ.edge['file01']['Bob'][0]['weight'], 1)
        self.assertEqual(len(summ.edge['Alice']), 1)
        self.assertEqual(len(summ.edge['file01']), 2)
        self.assertEqual(len(summ.edge['Bob']), 1)
        # Not summing weights
        nosum = self.now.collapse_edges()
        self.assertIsInstance(nosum, multigraph.MultiGraphPlus)
        self.assertEqual(nosum.edge['Alice']['file01'][0]['weight'], 2)
        self.assertEqual(nosum.edge['file01']['Bob'][0]['weight'], 1)
        self.assertEqual(len(nosum.edge['Alice']), 1)
        self.assertEqual(len(nosum.edge['file01']), 2)
        self.assertEqual(len(nosum.edge['Bob']), 1)

    def test_some_weight(self):
        """Does the method perform correctly when some edges have weights, while others don't?"""
        mgw = self.mgw
        mgw.add_edge(2, 3)  # Add non-weighted edge
        # Sum weights
        somew_sum = mgw.collapse_edges(sum_weights=True)
        self.assertIsInstance(somew_sum, multigraph.MultiGraphPlus)
        self.assertEqual(somew_sum.edge[1][2][0]['weight'], 5)
        self.assertEqual(somew_sum.edge[2][3][0]['weight'], 5)

        # Don't sum weights
        somew_nosum = mgw.collapse_edges(sum_weights=False)
        self.assertIsInstance(somew_nosum, multigraph.MultiGraphPlus)
        self.assertEqual(somew_nosum.edge[1][2][0]['weight'], 2)
        self.assertEqual(somew_nosum.edge[2][3][0]['weight'], 2)

    def test_eattr(self):
        """Are edge attributes retained?"""
        mg = self.now.collapse_edges()
        self.assertIsInstance(mg, multigraph.MultiGraphPlus)
        # Looking at Alice, contains a list attribute
        self.assertIsInstance(mg.edge['Alice'], dict)
        ad = {'file01': {0: {'weight': 2,
                             'type': ['commit', 'commit'],
                             'date': ['Jan 3', 'Jan 5'],
                             'changed_lines': [5, 18, 38, 44, 3, 5, 23, 67]}}}
        self.assertDictEqual(mg.edge['Alice'], ad)
        # Looking at Bob, contains a unique attribute
        bd = {'file01': {0: {'weight': 1,
                             'type': 'issue',  # Is this what we want ?? Should they just be stored atomically?
                             'date': 'Jan 16',
                             'importance': 'high'}}}
        self.assertIsInstance(mg.edge['Bob'], dict)
        self.assertDictEqual(mg.edge['Bob'], bd)
        # Looking at file01, contains multiple edges
        fd = {'Alice':  ad['file01'], 'Bob': bd['file01']}
        self.assertIsInstance(mg.edge['file01'], dict)
        self.assertDictEqual(mg.edge['file01'], fd)

    def test_diff_attr(self):
        """Are edge attributes retained properly, even when they aren't the same?"""
        # Sum the weights
        diff_attr = self.diff.collapse_edges(sum_weights=True)
        self.assertIsInstance(diff_attr, multigraph.MultiGraphPlus)
        # Looking at Charlie, contains 3 unique attributes
        cd = {'file02': {0: {'weight': 7,
                             'type': ['commit', 'issue', 'review'],
                             'date': ['Jan 1', 'Jan 2', 'Jan 5'],
                             'changed_lines': [1, 2],
                             'importance': 'high',
                             'status': 'PASS'}}}
        self.assertIsInstance(diff_attr.edge['Charlie'], dict)
        self.assertDictEqual(diff_attr.edge['Charlie'], cd)

        # Look at Dawn, adds an attribute which wasn't originally there
        dd = {'file02': {0: {'weight': 6,
                             'type': ['commit', 'issue', 'issue'],
                             'date': ['Jan 3', 'Jan 12', 'Jan 23'],
                             'changed_lines': [1, 2, 3],
                             'importance': ['low', 'high']}}}
        self.assertIsInstance(diff_attr.edge['Dawn'], dict)
        self.assertDictEqual(diff_attr.edge['Dawn'], dd)

        # Look at Elise, where not all attributes will be in lists
        ed = {'file02': {0: {'weight': 2,
                             'type': 'commit',
                             'date': 'Jan 30',
                             'changed_lines': [4, 5]}}}
        self.assertIsInstance(diff_attr.edge['Elise'], dict)
        self.assertDictEqual(diff_attr.edge['Elise'], ed)

        # Look at file02, putting it all together
        f2d = {'Charlie':   cd['file02'],
               'Dawn':      dd['file02'],
               'Elise':     ed['file02']}
        self.assertDictEqual(diff_attr.edge['file02'], f2d)
        self.assertIsInstance(diff_attr.edge['file02'], dict)


if __name__ == '__main__':
    unittest.main(buffer=True)
