import datetime as dt
import re
import networkx as nx
from gitnet.gn_exceptions import InputError


# Working with Git Log date strings
def git_datetime(s):
    """
    Turns a git date string into a datetime object.
    :param s: A git-formatted date string.
    :return: A datetime object.
    """
    return dt.datetime.strptime(s,"%a %b %d %H:%M:%S %Y %z")


def reference_datetime(s):
    """
    Turns a Git date string, or a datetime object into a datetime.
    :param s: String or Datetime
    :return: Datetime
    """
    if type(s) is dt.datetime:
        ref_date = s
    elif type(s) is str:
        git_date_p = re.compile("[A-Z][a-z][a-z] [A-Z][a-z][a-z] \d\d? \d\d:\d\d:\d\d \d{4} -\d{4}")
        if bool(re.match(git_date_p, s)):
            ref_date = git_datetime(s)
        else:
            raise InputError("Unrecognized date format. match should be a Git formatted date string "
                             "(e.g. 'Mon Apr 18 00:59:02 2016 -0400') or a datetime object.")
    return ref_date


# Filtering functions.
def since(s, match):
    """
    A predicate determining if s is a date since match (inclusive).
    :param s: A Git date string (e.g.  Sat Apr 2 07:25:25 2016 -0600).
    :param match: A comparison date. Either a Git date string or a datetime object.
    :return: True or False.
    """
    dt_match = reference_datetime(match)
    return git_datetime(s) >= dt_match


def before(s, match):
    dt_match = reference_datetime(match)
    return git_datetime(s) <= dt_match


def sincex(s, match):
    dt_match = reference_datetime(match)
    return git_datetime(s) > dt_match


def beforex(s, match):
    dt_match = reference_datetime(match)
    return git_datetime(s) < dt_match


def filter_regex(s, match, mode="match"):
    """
    A predicate which determines whether "s" matches the regular expression "match".
    :param s: An input string which is compared to the regex pattern.
    :param match: A regular expression string.
    :param mode: Indicates whether regex should be matched ("match") or searched for ("search")
    :return: True or false.
    """
    pattern = re.compile(match)
    if mode == "match":
        return bool(re.match(pattern,s))
    elif mode == "search":
        return bool(re.search(pattern,s))


def filter_equals(x, match):
    """
    Determines whether x and match are equal. If x and match are both strings, match can be a regular expression.
    :param x: An input value.
    :param match: A reference value.
    :return: Are they the same?
    """
    if type(x) is str and type(match) is str:
        return filter_regex(x,match,mode = "match")
    else:
        return x == match


def filter_has(x,match):
    """
    Determines whether match is "in" x. If x and match are both strings, match can be a regular expression.
    :param x: An input value.
    :param match: A reference value.
    :return: Is match in x?
    """
    if type(x) is str and type(match) is str:
        return filter_regex(x,match,mode="search")
    try:
        return match in x
    except TypeError:
        return False


# Working with lists.
def most_common(lst):
    """
    Produces a list containing the most common entry in a list (more than one entry if there is a tie.)
    :param lst: A list of values.
    :return: A list of tuples, each containing a frequency integer and a value.
    """
    occurances = {}
    # Count occurences
    for i in lst:
        if i in occurances:
            occurances[i] += 1
        else:
            occurances[i] = 1
    s_list = []
    for j in occurances:
        if occurances[j] > 1:
            s_list.append((occurances[j],j))
    return sorted(s_list,reverse=True)


def most_occurrences(lst):
    """
    Produces the number of times the most common value appears
    :param lst: A list of values.
    :return: The occurences of the most common value.
    """
    occurances = {}
    max = 0
    m_common = []
    for i in lst:
        if i in occurances:
            occurances[i] += 1
        else:
            occurances[i] = 1
        if occurances[i] > max:
            max = occurances[i]
            m_common = [i]
        elif occurances[i] == max:
            m_common.append(i)
    return max


# Network Edge Generator Functions
def simple_edge(v1, v2, record, keep):
    """
    Creates an edge between to vertices, with an associated dictionary of properties.
    :param v1: The first vertex, any type.
    :param v2: The second vertex, any type.
    :param record: The current record in edge generation.
    :param keep: The edge attributes to be kept from the record.
    :return: An edge tuple, in format (id1, id2, {edge attribute dictionary})
    """
    properties = {k:v for k,v in record.items() if k in keep}
    return (v1,v2, properties)


def changes_edge(v1, v2, record, keep):
    """
    Creates an edge between an "any" and a CommitLog file ("file"), weighted by the number of lines changed
    in the file. Is a helper for Log.generate_edges().
    :param v1: The first vertex, any type.
    :param v2: Must be a file string (e.g. "my_dir/my_file.txt") as in CommitLog "files"
    :param record: The current record in edge generation.
    :param keep: The edge attributes to be kept from the record.
    :return: An edge tuple, in format (id1, id2, {edge attribute dictionary})
    """
    properties = {k:v for k,v in record.items() if k in keep}
    # Get file name and change weight
    split_change = ""
    for ch in record["changes"]:
        if ch[:len(v2)+1] == v2 + " ":
            split_change = ch.split("|")
            break
    if split_change == "":
        return (v1,v2,properties)
    fname = split_change[0].replace(" ","")
    assert(fname == v2)
    weight_str = split_change[1]
    if "Bin" in weight_str:
        properties["weight"] = 1
    else:
        weight = ""
        for char in weight_str:
            if char.isnumeric():
                weight += char
        if weight == "":
            weight = "0"
        properties["weight"] = int(weight)
    return (v1,v2,properties)

# Network Attribute Helper Functions

def author_file_node_colours(d):
    """
    Creates default colourings for an author/file bipartite network.
    :param d: The attribute dictionary for the node.
    :return: A colour string.

    Colours:
        Default: lightgrey
        Author: dodgerblue
        Python: tomato
        C (code): gold
        C (interface): goldenrod
    """
    if "type" not in d.keys():
        return "lightgrey"
    else:
        type = d["type"]
        if type == "author":
            return "dodgerblue"
        elif type == "files":
            if "id" not in d.keys():
                return "lightgrey"
            id = d["id"]
            if filter_regex(id,"\.py$",mode="search"):
                return "tomato"
            elif filter_regex(id,"\.cc$",mode="search"):
                return "gold"
            elif filter_regex(id, "\.h$", mode="search"):
                return "goldenrod"
            else:
                return "lightgrey"
        else:
            return "lightgrey"