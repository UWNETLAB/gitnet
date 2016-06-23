import unittest
import gitnet
from gitnet import helpers
import datetime as dt
import pytz
import subprocess as sub
import os


class DatetimeTests(unittest.TestCase):
    def setUp(self):
        sub.call(["cp", "-R", "small_network_repo.git", ".git"])
        self.good_path = os.getcwd()
        self.my_log = gitnet.get_log(self.good_path)

    def test_git_datetime(self):
        # Currently only used by write edges.
        self.my_log.write_edges("sample_datetime.txt", "author", "date", edge_attribute = ["author", "date"])
        with open("sample_datetime.txt", "r") as f:
            self.data = f.read().replace('\n', '')
        self.assertIn("Mon May 23 02:45:25 2016 -0400", self.data)
        sub.call(["rm", "-rf", "sample_datetime.txt"])

    def test_reference_datetime(self):
        # Unsure how to test beyond git_datetime testing.
        # There is no requirement to test for bad datetimes, since commits cannot be made with a bad datetime.
        pass

    def tearDown(self):
        sub.call(["rm", "-rf", ".git"])


class FilterTests(unittest.TestCase):
    def setUp(self):
        self.gdt1 = 'Thu Feb 4 09:13:45 2016 -0600'
        self.gdt2 = 'Sat Apr 2 07:25:25 2016 -0600'
        self.gdt3 = 'Fri Jun 10 23:03:00 2016 -0600'

        # -0600 from each
        tz = pytz.timezone("UTC")
        self.dt1 = dt.datetime(year=2016, month=2, day=4, hour=15, minute=13, second=45, microsecond=0, tzinfo=tz)
        self.dt2 = dt.datetime(year=2016, month=4, day=2, hour=13, minute=25, second=25, microsecond=0, tzinfo=tz)
        self.dt3 = dt.datetime(year=2016, month=6, day=11, hour=5, minute=3, second=0, microsecond=0, tzinfo=tz)

    def test_since(self):
        # Checking gitdatetimes work as expected
        self.assertFalse(helpers.since(self.gdt1, self.gdt2))
        self.assertTrue(helpers.since(self.gdt2, self.gdt2))
        self.assertTrue(helpers.since(self.gdt3, self.gdt2))

        # Checking function works with datetimes as second argument
        self.assertFalse(helpers.since(self.gdt1, self.dt2))
        self.assertTrue(helpers.since(self.gdt2, self.dt2))
        self.assertTrue(helpers.since(self.gdt3, self.dt2))

    def test_before(self):
        # Checking gitdatetimes work as expected
        self.assertTrue(helpers.before(self.gdt1, self.gdt2))
        self.assertTrue(helpers.before(self.gdt2, self.gdt2))
        self.assertFalse(helpers.before(self.gdt3, self.gdt2))

        # Checking function works with datetimes as second argument
        self.assertTrue(helpers.before(self.gdt1, self.dt2))
        self.assertTrue(helpers.before(self.gdt2, self.dt2))
        self.assertFalse(helpers.before(self.gdt3, self.dt2))

    def test_sincex(self):
        # Checking gitdatetimes work as expected
        self.assertFalse(helpers.sincex(self.gdt1, self.gdt2))
        self.assertFalse(helpers.sincex(self.gdt2, self.gdt2))
        self.assertTrue(helpers.sincex(self.gdt3, self.gdt2))

        # Checking function works with datetimes as second argument
        self.assertFalse(helpers.sincex(self.gdt1, self.dt2))
        self.assertFalse(helpers.sincex(self.gdt2, self.dt2))
        self.assertTrue(helpers.sincex(self.gdt3, self.dt2))

    def test_beforex(self):
        # Checking gitdatetimes work as expected
        self.assertTrue(helpers.beforex(self.gdt1, self.gdt2))
        self.assertFalse(helpers.beforex(self.gdt2, self.gdt2))
        self.assertFalse(helpers.beforex(self.gdt3, self.gdt2))

        # Checking function works with datetimes as second argument
        self.assertTrue(helpers.beforex(self.gdt1, self.dt2))
        self.assertFalse(helpers.beforex(self.gdt2, self.dt2))
        self.assertFalse(helpers.beforex(self.gdt3, self.dt2))

    def test_filter_regex(self):
        # Checking ?
        reg2 = "ab?c"
        self.assertTrue(helpers.filter_regex("ac", reg2))
        self.assertTrue(helpers.filter_regex("abc", reg2))
        self.assertFalse(helpers.filter_regex("abbc", reg2))

        # Checking *
        reg1 = "ab*c"
        self.assertTrue(helpers.filter_regex("ac", reg1))
        self.assertTrue(helpers.filter_regex("abc", reg1))
        self.assertTrue(helpers.filter_regex("abbc", reg1))

        # Checking +
        reg3 = "ab+c"
        self.assertFalse(helpers.filter_regex("ac", reg3))
        self.assertTrue(helpers.filter_regex("abc", reg3))
        self.assertTrue(helpers.filter_regex("abbc", reg3))

        # Checking |
        reg4 = "Alice|Bob"
        self.assertTrue(helpers.filter_regex("Alice", reg4))
        self.assertTrue(helpers.filter_regex("Bob", reg4))
        self.assertFalse(helpers.filter_regex("Charlie", reg4))

        # Checking .
        reg5 = "Alic. Smith"
        self.assertFalse(helpers.filter_regex("Alice", reg5))
        self.assertTrue(helpers.filter_regex("Alice Smith", reg5))
        self.assertTrue(helpers.filter_regex("Alicb Smith", reg5))
        reg5 = "Alice.*"
        self.assertTrue(helpers.filter_regex("Alice", reg5))
        self.assertTrue(helpers.filter_regex("Alice blah", reg5))
        self.assertTrue(helpers.filter_regex("Alice Smith", reg5))

    def test_filter_equals(self):
        stra1 = "Alice"
        stra2 = "Alice"
        strb = "Bobby"
        strc1 = "Chaaarlie"
        strc2 = "Cha*rlie"
        strc3 = "Chrlie"

        # Checking simple strings with each other
        self.assertTrue(helpers.filter_equals(stra1, stra2))
        self.assertFalse(helpers.filter_equals(stra1, strb))

        # Checking strings with regular expressions
        self.assertTrue(helpers.filter_equals(strc1, strc2))
        self.assertTrue(helpers.filter_equals(strc3, strc2))

        # Checking other types
        self.assertTrue(helpers.filter_equals(1,1))
        self.assertFalse(helpers.filter_equals(123, 3))

    def test_filter_has(self):
        xstr = "Hello my name is Alice"
        mstr = "Alice"
        lst = [1, 'a', 'Hello World', "Alice"]

        # Checking strings act as expected
        self.assertFalse(helpers.filter_has(mstr, xstr))
        self.assertTrue(helpers.filter_has(xstr, mstr))

        # Checking strings and lists act as expected
        self.assertFalse(helpers.filter_has(mstr, lst))
        self.assertFalse(helpers.filter_has(xstr, lst))
        self.assertTrue(helpers.filter_has(lst, mstr))
        self.assertFalse(helpers.filter_has(lst, xstr))

        # Checking other types work as expected
        self.assertFalse(helpers.filter_has(xstr, 1))
        self.assertFalse(helpers.filter_has(lst, 2))
        self.assertTrue(helpers.filter_has(lst, 1))


class ListTests(unittest.TestCase):
    def setUp(self):
        self.norep = ['a', 'b', 'c']
        self.repa = ['a', 'a', 'b', 'c']
        self.repab = ['a', 'b', 'a', 'b', 'c', 'd']
        self.lofi = [1,2,3]
        self.lofl = [[2,3], ['a','b'], [1,'c']]

    def test_most_common(self):
        """Does the most_common() helper function work properly?"""
        # Do the defaults work?
        self.assertIsInstance(helpers.most_common(self.norep), list)
        self.assertEqual(helpers.most_common(self.norep),[])
        self.assertSetEqual(set(helpers.most_common(self.repa)), {(2, 'a')})
        self.assertSetEqual(set(helpers.most_common(self.repab)), {(2, 'a'), (2, 'b')})
        self.assertSetEqual(set(helpers.most_common(['a', 'b', 'c', 'a', 'b', 'a'])), {(3, 'a')})

        # Do other values of n work?
        lst = ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'd', 'd', 'd', 'a', 'e']
        self.assertSetEqual(set(helpers.most_common(lst, 1)), {(4, 'a')})
        self.assertSetEqual(set(helpers.most_common(lst, 2)), {(4, 'a'), (3, 'd')})
        self.assertSetEqual(set(helpers.most_common(lst, 3)), {(4, 'a'), (3, 'd'), (2, 'b'), (2, 'c')})
        # self.assertEqual(helpers.most_common(lst, 4), [(4, 'a'), (3, 'd'), (2, 'b'), (2, 'c')])

    def test_most_occurrences(self):
        self.assertIsInstance(helpers.most_occurrences(self.norep), int)
        self.assertEqual(helpers.most_occurrences(self.norep), 1)
        self.assertEqual(helpers.most_occurrences(self.repa), 2)
        self.assertEqual(helpers.most_occurrences(self.repab), 2)

    def test_lst_scd_str(self):
        self.assertIsInstance(helpers.list_scd_str(self.norep), str)
        self.assertEqual(helpers.list_scd_str(self.norep), 'a;b;c')
        self.assertEqual(helpers.list_scd_str(self.lofi), '1;2;3')
        self.assertEqual(helpers.list_scd_str(self.lofl), '[2, 3];[\'a\', \'b\'];[1, \'c\']')


class EdgeGenTests(unittest.TestCase):
    def setUp(self):
        # Set up Repo One
        sub.call(["cp", "-R", "repo_one.git", ".git"])
        good_path = os.getcwd()
        my_log = gitnet.get_log(good_path)
        self.r1 = my_log.collection['fc3527c']
        self.r2 = my_log.collection['44b4c72']
        self.r3 = my_log.collection['51ba020']
        # for record in my_log.collection:
        #     print(record)
        #     print(my_log.collection[record])

        # Set up NX Repo

    def test_simple_edge(self):
        # Check return type
        self.assertIsInstance(helpers.simple_edge("Alice", "file01", self.r3, ['date']), tuple)

        # Check return values
        self.assertTupleEqual(helpers.simple_edge("Alice", "readme.md", self.r1, ['date']),
                              ("Alice", "readme.md", {'date': 'Fri May 6 14:41:25 2016 -0400'} ))
        self.assertTupleEqual(helpers.simple_edge("Alice", "raw_logs.txt", self.r2, ['date']),
                              ("Alice", "raw_logs.txt", {'date': 'Fri May 6 15:41:25 2016 -0400'}))
        self.assertTupleEqual(helpers.simple_edge("Bob", "readme.md", self.r3, ['date']),
                              ("Bob", "readme.md", {'date': 'Fri May 6 14:50:22 2016 -0400'}))

    def test_change_edge(self):
        # Check return type
        self.assertIsInstance(helpers.changes_edge('Alice', 'file78', self.r3, ['date']), tuple)

        # Check return values
        self.assertTupleEqual(helpers.changes_edge('Alice', 'file78', self.r3, ['date']),
                              ("Alice", 'file78', {'date': 'Fri May 6 14:50:22 2016 -0400'}))


        # Checking Bin execution
        sub.call(["rm","-rf",".git"])
        sub.call(["cp", "-R", "repo_nx.git", ".git"])
        good_path = os.getcwd()
        nx_log = gitnet.get_log(good_path)
        nxr1 = nx_log.collection['1dc1602']
        self.assertTupleEqual(helpers.changes_edge('Dan Schult', 'examples/drawing/knuth_miles.txt.gz', nxr1, ['date']),
                              ('Dan Schult', 'examples/drawing/knuth_miles.txt.gz',
                               {'date': 'Fri Aug 7 11:02:04 2015 -0400',
                                'weight': 1}))

        self.assertTupleEqual(helpers.changes_edge('Dan Schult', 'networkx/algorithms/threshold.py', nxr1, ['date']),
                              ('Dan Schult', 'networkx/algorithms/threshold.py',
                               {'date': 'Fri Aug 7 11:02:04 2015 -0400',
                                'weight': 910}))

    def tearDown(self):
        sub.call(["rm", "-rf", ".git"])


class TestNetAttr(unittest.TestCase):
    def setUp(self):
        self.a_attr = {'id': 'Alice',
                       'type': 'author',
                       'email': 'alice@gmail.com'}
        self.b_attr = {'id': 'Bobby',
                       'type': 'author',
                       'email': 'bobby@gmail.com'}
        self.f1_attr = {'id': 'f01.py',
                        'type': 'files'}
        self.f2_attr = {'id': 'f02.cc',
                        'type': 'files'}
        self.f3_attr = {'id': 'f03.h',
                        'type': 'files'}
        self.f4_attr = {'id': 'f04.txt',
                        'type': 'files'}

    def test_basic(self):
        """Ensure the function returns a string"""
        res = helpers.author_file_node_colours(self.a_attr)
        self.assertIsInstance(res, str)

    def test_no_type(self):
        """Are nodes with no type assigned lightgrey?"""
        notype = {'id': 'mystery',
                  'email': 'abc@alphabet.com'}
        res = helpers.author_file_node_colours(notype)
        self.assertEqual(res, "lightgrey")

    def test_authors(self):
        """Are authors assigned the correct colour?"""
        a_res = helpers.author_file_node_colours(self.a_attr)
        b_res = helpers.author_file_node_colours(self.b_attr)

        self.assertEqual(a_res, "dodgerblue")
        self.assertEqual(b_res, "dodgerblue")

    def test_files(self):
        """Do files of the types .py, .cc, .h, etc give the correct colours?"""
        # Setting up results
        res1 = helpers.author_file_node_colours(self.f1_attr)
        res2 = helpers.author_file_node_colours(self.f2_attr)
        res3 = helpers.author_file_node_colours(self.f3_attr)
        res4 = helpers.author_file_node_colours(self.f4_attr)

        self.assertEqual(res1, "tomato")
        self.assertEqual(res2, "gold")
        self.assertEqual(res3, "goldenrod")
        self.assertEqual(res4, "lightgrey")

    def test_files_noid(self):
        """Are file nodes with no id assigned lightgrey?"""
        noid = {'type': 'files'}
        res = helpers.author_file_node_colours(noid)

        self.assertEqual(res, "lightgrey")

    def test_not_aorf(self):
        """Are nodes whose type is neither files nor author assigned lightgrey?"""
        fnora = {'id': 'Uwaterloo',
                 'type': 'university'}
        res = helpers.author_file_node_colours(fnora)

        self.assertEqual(res, "lightgrey")

if __name__ == '__main__':
    unittest.main(buffer=True)
