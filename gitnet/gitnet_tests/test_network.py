import unittest
from gitnet import gn_multigraph


class CollapseEdgesTest(unittest.TestCase):
    """Tests for the collapse_edges() method within gn_multigraph.py"""
    # A simple graph with weights
    mgw = gn_multigraph.MultiGraphPlus()
    mgw.add_edge(1, 2, weight=3)
    mgw.add_edge(1, 2, weight=2)
    mgw.add_edge(2, 3, weight=4)

    # A graph with no weights, but other similar attributes
    now = gn_multigraph.MultiGraphPlus()
    now.add_edge('Alice', 'file01', type='commit', date='Jan 3', changed_lines=[5,18,38,44])
    now.add_edge('file01', 'Alice', type='commit', date='Jan 5', changed_lines=[3,5,23,67])
    now.add_edge('file01', 'Bob', type='issue', date='Jan 16', importance='high')

    # A graph whose edges have weights and other different attributes
    diff = gn_multigraph.MultiGraphPlus()
    diff.add_edge('Charlie', 'file02', weight=2, type='commit', date='Jan 1', changed_lines=[1, 2])
    diff.add_edge('Charlie', 'file02', weight=1, type='issue', date='Jan 2', importance='high')
    diff.add_edge('Charlie', 'file02', weight=4, type='review', date='Jan 5', status='PASS')
    diff.add_edge('Dawn', 'file02', weight=3, type='commit', date='Jan 3', changed_lines=[1, 2, 3])
    diff.add_edge('Dawn', 'file02', weight=1, type='issue', date='Jan 12', importance='low')
    diff.add_edge('Dawn', 'file02', weight=2, type='issue', date='Jan 23', importance='high')
    diff.add_edge('Elise', 'file02', weight=2, type='commit', date='Jan 30', changed_lines=[4, 5])

    def setup(self):
        pass

    def test_simple(self):
        """When sum_weights==False, or isn't provided, are weights calculated by adding number of edges?"""
        # sum_weights is made explicit
        sumwf_explicit = self.mgw.collapse_edges(sum_weights=False)
        self.assertIsInstance(sumwf_explicit, gn_multigraph.MultiGraphPlus)
        self.assertEqual(sumwf_explicit.edge[1][2][0]['weight'], 2)
        self.assertEqual(sumwf_explicit.edge[2][3][0]['weight'], 1)
        self.assertEqual(len(sumwf_explicit.edge[1]), 1)
        self.assertEqual(len(sumwf_explicit.edge[2]), 2)
        self.assertEqual(len(sumwf_explicit.edge[3]), 1)

        # sum_weights is left to the default
        sumwf = self.mgw.collapse_edges()
        self.assertIsInstance(sumwf, gn_multigraph.MultiGraphPlus)
        self.assertEqual(sumwf.edge[1][2][0]['weight'], 2)
        self.assertEqual(sumwf.edge[2][3][0]['weight'], 1)
        self.assertEqual(len(sumwf.edge[1]), 1)
        self.assertEqual(len(sumwf.edge[2]), 2)
        self.assertEqual(len(sumwf.edge[3]), 1)

    def test_simple_sum_weights(self):
        """When sum_weights==True, are weights added?"""
        sumwt = self.mgw.collapse_edges(sum_weights=True)
        self.assertIsInstance(sumwt, gn_multigraph.MultiGraphPlus)
        self.assertEqual(sumwt.edge[1][2][0]['weight'], 5)
        self.assertEqual(sumwt.edge[2][3][0]['weight'], 4)
        self.assertEqual(len(sumwt.edge[1]), 1)
        self.assertEqual(len(sumwt.edge[2]), 2)
        self.assertEqual(len(sumwt.edge[3]), 1)

    def test_no_weight(self):
        """Is the absence of a weight attribute handled correctly? (Default to 1)?"""
        # Summing the weights
        sum = self.now.collapse_edges(sum_weights=True)
        self.assertIsInstance(sum, gn_multigraph.MultiGraphPlus)
        self.assertEqual(sum.edge['Alice']['file01'][0]['weight'], 2)
        self.assertEqual(sum.edge['file01']['Bob'][0]['weight'], 1)
        self.assertEqual(len(sum.edge['Alice']), 1)
        self.assertEqual(len(sum.edge['file01']), 2)
        self.assertEqual(len(sum.edge['Bob']), 1)
        # Not summing weights
        nosum = self.now.collapse_edges()
        self.assertIsInstance(nosum, gn_multigraph.MultiGraphPlus)
        self.assertEqual(nosum.edge['Alice']['file01'][0]['weight'], 2)
        self.assertEqual(nosum.edge['file01']['Bob'][0]['weight'], 1)
        self.assertEqual(len(nosum.edge['Alice']), 1)
        self.assertEqual(len(nosum.edge['file01']), 2)
        self.assertEqual(len(nosum.edge['Bob']), 1)

    def test_some_weight(self):
        """Does the method perform correctly when some edges have weights, while others don't?"""
        mgw = self.mgw
        mgw.add_edge(2,3) # Add non-weighted edge
        # Sum weights
        somew_sum = mgw.collapse_edges(sum_weights=True)
        self.assertIsInstance(somew_sum, gn_multigraph.MultiGraphPlus)
        self.assertEqual(somew_sum.edge[1][2][0]['weight'],5)
        self.assertEqual(somew_sum.edge[2][3][0]['weight'],5)

        # Don't sum weights
        somew_nosum = mgw.collapse_edges(sum_weights=False)
        self.assertIsInstance(somew_nosum, gn_multigraph.MultiGraphPlus)
        self.assertEqual(somew_nosum.edge[1][2][0]['weight'], 2)
        self.assertEqual(somew_nosum.edge[2][3][0]['weight'], 2)

    def test_eattr(self):
        """Are edge attributes retained?"""
        mg = self.now.collapse_edges()
        self.assertIsInstance(mg, gn_multigraph.MultiGraphPlus)
        # Looking at Alice, contains a list attribute
        self.assertIsInstance(mg.edge['Alice'], dict)
        AD = {'file01': {0: {'weight': 2,
                             'type': ['commit', 'commit'],
                             'date':['Jan 3', 'Jan 5'],
                             'changed_lines': [5, 18, 38, 44, 3, 5, 23, 67]}}}
        self.assertDictEqual(mg.edge['Alice'], AD)
        # Looking at Bob, contains a unique attribute
        BD = {'file01': {0: {'weight': 1,
                             'type': 'issue', # Is this what we want ?? Should they just be stored atomically?
                             'date':'Jan 16',
                             'importance': 'high'}}}
        self.assertIsInstance(mg.edge['Bob'], dict)
        self.assertDictEqual(mg.edge['Bob'],BD)
        # Looking at file01, contains multiple edges
        FD = {'Alice':  AD['file01'], 'Bob': BD['file01']}
        self.assertIsInstance(mg.edge['file01'], dict)
        self.assertDictEqual(mg.edge['file01'], FD)

    def test_diff_attr(self):
        """Are edge attributes retained properly, even when they aren't the same?"""
        # Sum the weights
        diff_attr = self.diff.collapse_edges(sum_weights=True)
        self.assertIsInstance(diff_attr, gn_multigraph.MultiGraphPlus)
        # Looking at Charlie, contains 3 unique attributes
        cd = {'file02': {0: {'weight': 7,
                             'type': ['commit', 'issue', 'review'],
                             'date': ['Jan 1', 'Jan 2', 'Jan 5'],
                             'changed_lines': [1,2],
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
        ed = {'file02': {0: {'weight':2,
                             'type': 'commit',
                             'date': 'Jan 30',
                             'changed_lines': [4,5]}}}
        self.assertIsInstance(diff_attr.edge['Elise'], dict)
        self.assertDictEqual(diff_attr.edge['Elise'], ed)

        # Look at file02, putting it all together
        f2d = {'Charlie':   cd['file02'],
               'Dawn':      dd['file02'],
               'Elise':     ed['file02']}
        self.assertDictEqual(diff_attr.edge['file02'], f2d)
        self.assertIsInstance(diff_attr.edge['file02'], dict)


class NodeMergeTest(unittest.TestCase):
    """Tests for the node_merge() method within gn_multigraph.py"""
    mg = gn_multigraph.MultiGraphPlus()
    mg.add_node('Alice', attr_dict={'id': 'a01',
                                    'email': 'alice@gmail.com',
                                    'phone': '1(888)123-4567',
                                    'type': 'author',
                                    'records': ['hash1', 'hash2'],
                                    'affiliations': ['Uwaterloo', 'Networks Lab']})
    mg.add_node('Alice Smith', attr_dict={'id': 'a02',
                                          'email': 'alice@gmail.ca',
                                          'type': 'author',
                                          'colour': 'blue',
                                          'records':['hash3', 'hash4'],
                                          'languages': ['Python', 'C']})
    mg.add_edge('Alice', 'file01', date='Jan 1', style='dotted')
    mg.add_edge('Alice Smith', 'file02', date='Jan 2', type='commit')
    mg_merged = mg.node_merge('Alice Smith', 'Alice', show_warning=False)

    def setUp(self):
        pass

    def test_basic_res(self):
        """Ensures the results of the method are appropriate"""
        mg_merged = self.mg_merged
        # Checking Return Value
        self.assertIsInstance(mg_merged, gn_multigraph.MultiGraphPlus)
        # Checking Nodes
        self.assertEqual(self.mg.number_of_nodes(), 4) # Checking before
        self.assertEqual(mg_merged.number_of_nodes(), 3)
        self.assertEqual(set(mg_merged.nodes()), {'Alice Smith', 'file01', 'file02'})
        self.assertNotIn('Alice', mg_merged.nodes())
        # Checking Edges
        self.assertEqual(self.mg.number_of_edges(), 2) # Checking before
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
        self.assertIsInstance(mg_merged, gn_multigraph.MultiGraphPlus)
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
        self.assertIsNotNone(mg_merged.node['Alice Smith']) # Keep node1?

    def test_edge_attr(self):
        """Does the method retain edge attributes?"""
        mg = self.mg
        mg_merged = self.mg_merged
        node1 = 'Alice Smith'
        node2 = 'Alice'
        # Checking if each in the original graph has the same edges as its corresponding edge in the merged graph
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
        pass

    def test_mult_edge(self):
        """Are multiple edges handled correctly?
         Ex. A1->B, A2->B. Then merge A1 and A2. """
        pass

    def test_show_warn(self):
        """Does the show_warning parameter act as anticipated"""
        pass

    def test_warn_owrt(self):
        """Is the overwrite warning(print statement) printed at the right time?"""
        pass

    def test_errors(self):
        """Are errors being raised at the correct times?"""
        pass

if __name__ == '__main__':
    unittest.main()
