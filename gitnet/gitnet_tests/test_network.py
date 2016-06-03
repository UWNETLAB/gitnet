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

if __name__ == '__main__':
    unittest.main()
