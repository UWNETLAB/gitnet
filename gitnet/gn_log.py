import pandas as pd
import networkx as nx
import datetime as dt
import warnings
import copy
from gitnet.gn_helpers import git_datetime, before, beforex, since, sincex, filter_has, filter_equals
from gitnet.gn_network import simple_edge

class Log(object):
    """
    Log is the basic class for the back end of gitnet. The Log class, and other classes which inherit its features,
    store all of the data retrieved by gitnet. Log has methods to describe, export, and model the data it contains.
    """

    def __init__(self, dofd = {}, source = None, path = None, key_type = None, filters = []):
        """
        Initializes the Log with a timestamp. Other fields default to {} or none unless otherwise specified.
        Log objects should be passed a dictionary of dictionaries after initialization, or entries should be
        added to the empty dictionary in self.collection.

        :param dofd: A dictionary of dictionaries, which becomes self.collection. Defaults to empty.
        :param source: A string passed by the parser indicating the source of the data.
        :param path: A string passed by the parser indicating the path from which the data was accessed.
        :param key_type: A string passed by the parser indicating how data is keyed in the dicitonary (e.g. by hash.)
        :param filters: A list of strings summarizing how the Log has been filtered (using filter and ignore methods.)
        :var self.tags: Tags are generated using the get_tags method.
        """
        self.collection = dofd
        self.timestamp = str(dt.datetime.now())
        self.source = source
        self.path = path
        self.key_type = key_type
        self.filters = filters
        # This must be updated as tags/subclasses are added. Ideally, this would be housed within each subclass.
        self.tags = self.get_tags()

    def __iter__(self):
        """
        Log iterates upon its core data set, which is a dictionary of dictionaries.
        """
        return iter(self.collection)

    def __getitem__(self, item):
        """
        Makes Log subscriptable.
        """
        return self.collection[item]

    def __str__(self):
        """
        A basic summary of the Log. For a more detailed report (which analyzes record contents) use the .describe method.
        """
        return "Log containing {} records from {} created at {}.".format(len(self.collection),self.source,self.timestamp)

    def __len__(self):
        """
        The number of records in self.collection.
        """
        return len(self.collection)

    def get_tags(self):
        """
        For the base Log class, tags defaults to an empty list. Log subclasses have alternate get_tags methods, which
        specify the expected data points in their core data sets, and give a preferred order for displaying the data
        (i.e. in a tabular format.)
        :return: An empty list of tags.
        """
        return []

    def attributes(self):
        """
        A method for determining what data has been recorded in this commit log.
        :return: A sorted list containing every key present in the Log's records. For example, the attributes for
        a local commit log would contain hashes ("hash"), author name ("author"), author email ("email"), etc.
        If the self.tags attribute has been defined for this object, tags appear by their order in self.tags. Any
        unrecognized tags will be added at the end.
        """
        attr = set()
        # Add every key in the collection to a set object.
        for record in self.collection:
            attr = attr.union(self.collection[record].keys())
        # Tracking attributes
        attr_list = []
        # For every tag defined for the subclass, add to the list of attributes in order, and remove from set.
        for tag in self.tags:
            if tag in attr:
                attr.remove(tag)
                attr_list.append(tag)
        # If there are any tags left in the set (i.e. ones not specified for the subclass),
        #   add them to the end of the list (sorted).
        if len(attr) > 0:
            attr_list = attr_list + sorted(list(attr))
        return attr_list

    def describe(self):
        """
        A method which provides a description of the contents of the log. More detailed descriptions are implemented
        for individual subclasses.
        """
        print(self)
        print(self.path)
        if len(self.filters) != 0:
            print("Filters:")
            for f in self.filters:
                print("\t",f)
        pass

    def browse(self):
        """
        Interactively prints the contents of the Log collection, one commit at a time.
        :return: None
        """
        for key in self.collection.keys():
            print("----- {} -----".format(key))
            for rkey in self.collection[key].keys():
                print("--- {} ---".format(rkey))
                if type(self.collection[key][rkey]) in [str,int,bool,float]:
                    print(self.collection[key][rkey])
                elif type(self.collection[key][rkey]) == list:
                    for s in self.collection[key][rkey]:
                        print(s)
            if input("\nAnother? [press enter to continue, or press q to quit]\n") == "q":
                break

    def filter(self, tag, fun, match, negate = False, helper = None, summary = None):
        """
        A method which creates a new Log, containing only records which match certain criteria.
        :param tag: Denotes the tag by which the Log should be filtered. ("ALL" searches every value.)
        :param fun: A string denoting which predicate function to use.
        :param match: A string which the predicate function uses for comparison.
        :param negate: If negate is set to true, only entries which do not match will be kept.
        :param helper: Passing a function object over-rides 'fun'.
        :param summary: An optional summary string describing the filter operation. Recommended when using a custom
        helper function.
        :return: A new Log object identical to self but with only matching records.

        Details:
        Comparisons are usually made in the following way: fun(self.collection[sha][tag],match). This pattern should
        be followed when using custom helper functions.

        Predicates currently implemented:
            - "equals" (Does the [tag] value exactly equal match? e.g. self.filter("author","equals","Jane"))
                - If both values are strings, match can be a regular expression.
            - "has" (Is match "in" the [tag] value? e.g. self.filter("email","has","@gmail.com"))
                - If both values are strings, match can be a regular expression.
            - Comparison operations. The values of tag, and match, must be comparable with >, and <. Note that unless
            you have explicitly converted date strings to datetime objects (or something similar), these comparisons
            are not valid for date strings.
                - "<" tag value less than match.
                - "<=" tag value less than or equal to match.
                - ">" tag value greater than match.
                - ">=" tag value greater than or equal to match.
            - Datetime comparisons. Note that tag must be date, and match must be a Git-formatted time (such as
                "Mon Apr 8 00:59:02 2016 -0400")
                - "since" (Is the date since match? Inclusive.)
                - "sincex" (Is the date since match? Exclusive.)
                - "before" (Is the date before match? Inclusive.)
                - "beforex" (Is the date before match? Exclusive.)

        Note that if a keyed value is a list, every item in the list is checked.

        Examples:
        my_log.filter("email", "equals", "bob@gmail.com")
        my_log.filter("email", "has", "@gmail.com")
        my_log.filter("email", "has", "@gmail.c[oa]m?")
        my_log.filter("date", "since", "Fri May 6 15:41:25 2016 -0400")
        """
        # This dictionary includes the currently built-in filtering predicates.
        fun_reference = {"equals" : filter_equals,
                         "has" : filter_has,
                         "<": lambda x, val: x < val,
                         "<=": lambda x, val: x < val or x == val,
                         ">": lambda x, val: x > val,
                         ">=": lambda x, val: x > val or x == val,
                         "since": since,
                         "sincex": sincex,
                         "before": before,
                         "beforex": beforex}
        if tag == "date" and fun in ("<", "<=", ">", ">="):
            warnings.warn("Dates have been compared alphabetically with {}, use Datetime comparisons to compare dates by time.".format(fun))
        # Make a copy of self
        new_log = copy.deepcopy(self)
        # Add filter summary to self.filters
        if summary is not None:
            filter_summary = summary
        else:
            filter_summary = "{} {} {} | Negate: {} | Helper: {}".format(tag,fun,match,negate,helper)
        new_log.filters.append(filter_summary)
        # Get the predicate for filtering, from custom helper parameter or helper dictionary.
        if callable(helper):
            use_fun = helper
        else:
            use_fun = fun_reference[fun]
        # Check every record for a match.
        for record in self.collection:
            keep = False
            # Check all tags.
            if tag == "any":
                for rkey in self.collection[record]:
                    if type(self.collection[record][rkey]) == list:
                        for item in self.collection[record][rkey]:
                            if use_fun(item,match):
                                keep = True
                                break
                    if use_fun(self.collection[record][rkey],match):
                        keep = True
                        break
            # Check a specific tag
            elif tag in self.collection[record].keys():
                if type(self.collection[record][tag]) == list:
                    for item in self.collection[record][tag]:
                        if use_fun(item, match):
                            keep = True
                            break
                if use_fun(self.collection[record][tag], match):
                    keep = True
            # Negate the check if required.
            if negate:
                keep = not(keep)
            # If the data point is not to be kept, remove the record from the copied collection.
            if not keep:
                del new_log.collection[record]
        return new_log

    def tsv(self, ignore = [], fname = None, empty_cols = False):
        """
        Converts the Log to a tab-delimited string (using a tab-delimted format is preferrable to CSV since this option
        does not change the content strings by removing commas).
        :param ignore: Tags included in this list of strings will be ignored.
        :param fname: If a file name is provided, the function will write to this file instead of to a string for output.
        :param empty_cols: If True, export will include all Log subclass tags, even if not collected, giving empty columns.
        :return: A tab-delimited dataset in string form (or a summary statement if a file name was provided.)
        """
        # Get the tags present in the Log.
        if empty_cols == True:
            types = self.tags
        else:
            types = self.attributes()
        types = list(filter(lambda s: s not in ignore, types))
        # The number of items that were forced to strings. If > 1 at return, raise a warning.
        num_forced = 0
        # The string to be output
        out = ""
        # If a filename is given, access the file.
        if fname != None:
            f = open(fname, "w", encoding="utf-8")
        # Add header line
        header = ""
        head_cur = 0
        for tag in types:
            head_cur += 1
            header = header + tag
            if head_cur != len(types):
                header = header + "\t"
            else:
                header = header + "\n"
        if fname != None:
            f.write(header)
        else:
            out = out + header
        # Create each line of output.
        for record in self.collection:
            line = ""
            tags_cur = 0
            # Add the value for each tag.
            for tag in types:
                tags_cur += 1
                if tag not in ignore:
                    # If the key is valid, add the value.
                    if tag in self.collection[record].keys():
                        cur_item = self.collection[record][tag]
                        # If the item is a simple string, add it.
                        if type(cur_item) == str:
                            line = line + cur_item
                        # If the item is a list, add each string in the list.
                        elif type(cur_item) == list:
                            list_cur = 0
                            for i in cur_item:
                                list_cur += 1
                                if type(i) == str:
                                    line = line + i
                                # Force a non-string to string.
                                else:
                                    line = line + str(i)
                                    num_forced += 1
                                if list_cur != len(cur_item):
                                    line = line + ";"
                        # If the item is neither a string nor a list, force it to a string.
                        else:
                            line = line + str(cur_item)
                            num_forced += 1
                    # Unless it is the last tag, add a separating tab.
                    if tags_cur != len(types):
                        line = line + "\t"
            # Give the line to string or file.
            line = line + "\n"
            if fname != None:
                f.write(line)
            else:
                out = out + line
        if num_forced > 0:
            warnings.warn("Non-string input forced to string {} time(s).".format(num_forced))
        if fname != None:
            f.close()
            out = "Data written to {}".format(fname)
        return out

    def df(self):
        """
        Converts the Log to a Pandas dataframe. Recommended method for analyzing attribute data in Python.
        :return: Pandas dataframe. Rows are commits by short-hash. Columns are commit attributes.
        """
        return pd.DataFrame.from_dict(self.collection, orient = "index")[self.attributes()]

    def vector(self,tag):
        """
        Returns a list containing all of the (keyless) values of a certain tag in the Log collection.
        :param tag: A collection tag. See subclass documentation for subclass-specific tags.
        :return: Returns a list of values (usually strings or numbers).
        """
        v = []
        for record in self.collection:
            if tag in self.collection[record].keys():
                value = self.collection[record][tag]
                if type(value) is list:
                    for i in value:
                        v.append(i)
                else:
                    v.append(value)
        return v

    def generate_edges(self, mode1, mode2, helper = simple_edge, keep = []):
        """
        Generates bipartite edges present in each Log record.
        :param mode1: A record attribute (tag), which becomes the first node type.
        :param mode2: A record attribute (tag), which becomes the second node type.
        :param helper: The function that computes the edges. Options are simple_edge (default) and changes_edge.
        :param keep: A list of attributes to keep as attributes of the edge.
        :return: A generator object containing edges and their weights.
        """
        for record in self.collection:
            cur = self.collection[record]
            if mode1 in cur.keys() and mode2 in cur.keys():
                # Set up mode one data for this record
                m1 = cur[mode1]
                if type(m1) not in [list,dict,set]:
                    m1 = [m1]
                # Set up mode one data for this record
                m2 = cur[mode2]
                if type(m2) not in [list, dict, set]:
                    m2 = [m2]
                # Yield edges
                for item1 in m1:
                    for item2 in m2:
                        yield helper(item1, item2, cur, keep)

    def generate_nodes(self, mode1, mode2, keep_atom1 = [], keep_vector1 = [], keep_atom2 = [], keep_vector2 = []):
        """
        Generates the bipartite nodes present in the Log object.
        :param mode1:
        :param mode2:
        :param keep_atom1: Atomic variables for mode1 nodes, recorded when a new node is added to the dictionary.
        :param keep_vector1: Variables for mode1 nodes, for which a new datapoint is recorded for every recurrence.
        :param keep_atom2: Atomic variables for mode2 nodes, recorded when a new node is added to the dictionary.
        :param keep_vector2: Variables for mode2 nodes, for which a new datapoint is recorded for every recurrence.
        :return: A list of tuples, i.e. ("node_id", {attribute_dictionary}).

        By default, each node should have a record in the following format:

        ("id_value",  {"id": "id_value", "type": mode, "records": [rkey1, rkey2, ..., rkeyn})

        With optional variables kept (i.e. keep_atom_1 etc. are not empty) format is as follows:

        ("id_value" : {"id": "id_value", "type": mode, "records": [rkey1, rkey2, ..., rkeyn},
         atom_tag_1: "atom_value_1", ..., atom_tag_n: "atom_value_n",
         vector_tag_1: [value_1_1, ..., value_1_m], ..., vector_tag_n: [value_n_1, ..., value_n_m])
        """
        nodes = {}
        for record in self.collection:
            cur = self.collection[record]
            if mode1 in cur.keys() and mode2 in cur.keys():
                # Set up mode one data for this record
                m1 = cur[mode1]
                if type(m1) not in [list, dict, set]:
                    m1 = [m1]
                # Set up mode one data for this record
                m2 = cur[mode2]
                if type(m2) not in [list, dict, set]:
                    m2 = [m2]
                # Yield node attributes
                for item1 in m1:
                    if item1 in nodes.keys():
                        nodes[item1]["records"].append(record)
                        for tag in keep_vector1:
                            if tag in cur.keys():
                                if tag not in nodes[item1].keys():
                                    nodes[item1][tag] = [cur[tag]]
                                elif tag in cur.keys():
                                    nodes[item1][tag].append(cur[tag])
                    else:
                        nodes[item1] = {"id":item1,"type":mode1,"records":[record]}
                        for tag in keep_atom1:
                            if tag in cur.keys():
                                nodes[item1][tag] = cur[tag]
                        for tag in keep_vector1:
                            if tag in cur.keys():
                                nodes[item1][tag] = [cur[tag]]
                for item2 in m2:
                    if item2 in nodes.keys():
                        nodes[item2]["records"].append(record)
                        for tag in keep_vector2:
                            if tag in cur.keys():
                                if tag not in nodes[item2].keys():
                                    nodes[item2][tag] = [cur[tag]]
                                elif tag in cur.keys():
                                    nodes[item2][tag].append(cur[tag])
                    else:
                        nodes[item2] = {"id": item2, "type": mode2, "records": [record]}
                        for tag in keep_atom2:
                            if tag in cur.keys():
                                nodes[item2][tag] = cur[tag]
                        for tag in keep_vector2:
                            if tag in cur.keys():
                                nodes[item2][tag] = [cur[tag]]
        if len(nodes) is 0:
            warnings.warn("Dictionary of node attributes is empty. Check that mode1 and mode2 names are valid tags.")
        node_tuple_list = []
        for n in nodes:
            node_tuple_list.append((n,nodes[n]))
        return node_tuple_list

    def generate_network(self, mode1, mode2, helper = simple_edge, edge_attributes = [], mode1_atom_attrs = [],
                         mode2_atom_attrs = [], mode1_vector_attrs = [], mode2_vector_attrs = []):
        GN = nx.MultiGraph()
        nodes = self.generate_nodes(mode1, mode2, keep_atom1=mode1_atom_attrs, keep_vector1=mode1_vector_attrs,
                                    keep_atom2=mode2_atom_attrs, keep_vector2=mode2_vector_attrs)
        for node in nodes:
            GN.add_node(node[0], node[1])
        edges = self.generate_edges(mode1, mode2, helper=helper, keep=edge_attributes)
        for edge in edges:
            GN.add_edges_from([(edge[0], edge[1], edge[2])])
        return GN

    def write_edges(self, fname, mode1, mode2, helper = simple_edge, keep = []):
        f = open(fname, "w", encoding="utf-8")
        # Define attributes
        attrs = ["id1", "id2", "weight", "date"] + keep
        # Write header
        cur = len(attrs)
        for colname in attrs:
            f.write(colname)
            if cur > 1:
                f.write(",")
                cur -= 1
            else:
                f.write("\n")
        # Write IDHash1,IDHash2,weight,month-day-year
        for edge in self.generate_edges(mode1,mode2,helper,keep):
            if "weight" in edge[2].keys():
                weight = edge[2]["weight"]
            else:
                weight = "NA"
            if "date" in edge[2].keys():
                date = git_datetime(edge[2]["date"]).date()
            f.write("{},{},{},{}-{}-{}".format(hash(edge[0]),hash(edge[1]),weight,date.month,date.day,date.year))
            for tag in keep:
                if tag in edge[2].keys():
                    f.write(",{}".format(edge[2][tag]))
                else:
                    f.write(",NA")
            f.write("\n")
        # Close file and print summary.
        f.close()
        print("Wrote edgelist with attributes to {}.".format(fname))

    def write_nodes(self, fname, mode1, mode2, keep_atom1 = [], keep_vector1 = [], keep_atom2 = [], keep_vector2 = []):
        # TODO update documentation
        """

        :param fname:
        :param mode1:
        :param mode2:
        :param keep_atom1:
        :param keep_vector1:
        :param keep_atom2:
        :param keep_vector2:
        :return:
        """
        f = open(fname, "w", encoding="utf-8")
        # Define attributes
        attrs = ["hashid","id","type"] + keep_atom1 + keep_vector1 + keep_atom2 + keep_vector2
        # Write header
        cur = len(attrs)
        for colname in attrs:
            f.write(colname)
            if cur > 1:
                f.write(",")
                cur -= 1
            else:
                f.write("\n")
        # Write IDHash, Name, type, ... [data]
        for node, values in self.generate_nodes(mode1,mode2,keep_atom1,keep_vector1,keep_atom2,keep_vector2):
            values["hashid"] = hash(node)
            ncur = len(attrs)
            for tag in attrs:
                if tag in values.keys():
                    val = values[tag]
                    if type(val) is int or type(val) is str:
                        f.write(str(val))
                    if type(val) is list:
                        valstring = ""
                        vcur = len(val)
                        for i in val:
                            valstring += str(i)
                            if vcur > 1:
                                valstring += ";"
                            vcur -= 1
                        f.write(valstring)
                else:
                    f.write("NA")
                if ncur > 1:
                    f.write(",")
                    ncur -= 1
                else:
                    f.write("\n")
        f.close()
        print("Wrote node attributes to {}.".format(fname))


def write_graphml(self, fname, mode1, mode2, helper=simple_edge, edge_attributes=[], mode1_atom_attrs=[],
                  mode2_atom_attrs=[], mode1_vector_attrs=[], mode2_vector_attrs=[]):
    pass