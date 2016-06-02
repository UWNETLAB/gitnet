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
    now.add_edge('Alice', 'file01', type='commit', date='Jan 3')
    now.add_edge('file01', 'Alice', type='commit', date='Jan 5')
    now.add_edge('file01', 'Bob', type='issue', date='Jan 16', importance='high')

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

    def test_eattr(self):
        """Are edge attributes retained?"""
        mg = self.now.collapse_edges()
        self.assertIsInstance(mg, gn_multigraph.MultiGraphPlus)
        # Looking at Alice
        self.assertIsInstance(mg.edge['Alice'], dict)
        AD = {'file01': {0: {'weight': 2,
                             'type': ['commit', 'commit'],
                             'date':['Jan 3', 'Jan 5']}}}
        self.assertDictEqual(mg.edge['Alice'], AD)
        # Looking at Bob
        BD = {'file01': {0: {'weight': 1,
                             'type': ['issue'], # Is this what we want ?? Should they just be stored atomically?
                             'date':['Jan 16'],
                             'importance': ['high']}}}
        self.assertIsInstance(mg.edge['Bob'], dict)
        self.assertDictEqual(mg.edge['Bob'],BD)
        # Looking at file01
        FD = {'Alice':  AD['file01'], 'Bob': BD['file01']}
        self.assertIsInstance(mg.edge['file01'], dict)
        self.assertDictEqual(mg.edge['file01'], FD)



if __name__ == '__main__':
    unittest.main()
