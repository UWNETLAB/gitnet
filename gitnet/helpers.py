# *********************************************************************************************
# Copyright (C) 2016 Jillian Anderson, Joel Becker, Steve McColl and Dr. John McLevey
#
# This file is part of the gitnet package developed for Dr John McLevey's Networks Lab
# at the University of Waterloo. For more information, see http://networkslab.org/gitnet/.
#
# gitnet is free software: you can redistribute it and/or modify it under the terms of a
# GNU General Public License as published by the Free Software Foundation. gitnet is
# distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with gitnet.
# If not, see <http://www.gnu.org/licenses/>.
# *********************************************************************************************

import datetime as dt
import re
from gitnet.exceptions import InputError

# Working with Git Log date strings
def datetime_git(s):
    """
    Turns a git date string into a datetime object.

    **Parameters**

    >*s* : `str`
    >> A git-formatted date string such as "Fri Jan 10 10:12:34 2016 -0400"

    **Return** `datetime`
    """
    return dt.datetime.strptime(s,"%a %b %d %H:%M:%S %Y %z")


def datetime_reference(s):
    """
    Turns a Git date string, or a datetime object into a datetime.

    **Parameters**

    >*s* : `str` or `datetime object`
    >> Either a git-formatted string such as "Wed Mar 4 20:00:00 2015 -0400" or a datetime object.

    **Return** `datetime`
    """
    if type(s) is dt.datetime:
        ref_date = s
    elif type(s) is str:
        git_date_p = re.compile("[A-Z][a-z][a-z] [A-Z][a-z][a-z] \d\d? \d\d:\d\d:\d\d \d{4} -\d{4}")
        if bool(re.match(git_date_p, s)):
            ref_date = datetime_git(s)
        else:
            raise InputError("Unrecognized date format. match should be a Git formatted date string "
                             "(e.g. 'Mon Apr 18 00:59:02 2016 -0400') or a datetime object.")
    return ref_date

# Filtering functions.
def filter_since(s, match):
    """
    A predicate function to determine if a date (`s`) has occurred since another date (`match`). This compares the dates
    inclusively, so if the dates are equal the function returns `True`.

    **Parameters**

    >*s* : `str`
    >> A git-formatted date string such as "Fri Jan 10 10:12:34 2016 -0400"

    >*match* : `str` or `datetime`
    >> Either a git-formatted date string such as "Sat Apr 2 07:25:25 2016 -0400" or a datetime object.

    **Return** `bool`
    > `True` if `s` is the same or a more recent date then `match`, otherwise `False`.
    """
    dt_match = datetime_reference(match)
    return datetime_git(s) >= dt_match


def filter_before(s, match):
    """
    A predicate function to determine if a date (`s`) occurred before another date (`match`). This compares the dates
    inclusively, so if the dates are equal the function will return `True`.

    **Parameters**

    >*s* : 'str'
    >> A git-formatted date string such as "Fri Jan 10 10:12:34 2016 -0400"

    >*match* : `str` or `datetime`
    >> Either a git-formatted date string such as "Sat Apr 2 07:25:25 2016 -0400" or a datetime object.

    **Return** `bool`
    > `True` if `s` is the same or a less recent date then `match`, otherwise `False`.
    """

    dt_match = datetime_reference(match)
    return datetime_git(s) <= dt_match


def filter_sincex(s, match):
    """
    A predicate function to determine if a date (`s`) has occurred since another date (`match`). This compares the dates
    exclusively, so if the dates are equal the function returns `False`.

    **Parameters**

    >*s* : `str`
    >> A git-formatted date string such as "Fri Jan 10 10:12:34 2016 -0400"

    >*match* : `str` or `datetime`
    >> Either a git-formatted date string such as "Sat Apr 2 07:25:25 2016 -0400" or a datetime object.

    **Return** `bool`
    > `True` if `s` is a more recent date then `match`, otherwise `False`.
    """
    dt_match = datetime_reference(match)
    return datetime_git(s) > dt_match


def filter_beforex(s, match):
    """
    A predicate function to determine if a date (`s`) occurred before another date (`match`). This compares the dates
    exclusively, so if the dates are equal the function will return `False`.

    **Parameters**

    >*s* : 'str'
    >> A git-formatted date string such as "Fri Jan 10 10:12:34 2016 -0400"

    >*match* : `str` or `datetime`
    >> Either a git-formatted date string such as "Sat Apr 2 07:25:25 2016 -0400" or a datetime object.

    **Return** `bool`
    > `True` if `s` is a less recent date then `match`, otherwise `False`.
    """
    dt_match = datetime_reference(match)
    return datetime_git(s) < dt_match


def filter_regex(s, match, mode="match"):
    """
    A predicate which determines whether `s` matches the regular expression `match`.

    **Parameters**

    >*s* : `str`
    >> An input string which is compared to the regex pattern.

    >*match* : `str`
    >> A regular expression string.

    *mode* : `str`
    >> A string to indicate whether the regular expression should be an exact match for `s` or if it should be searched
    for within `s`. Defaults to `"match"`, but may also be `"search"`.

    **Return** `bool`
    > `True` if `s` matches or contains the regular expression `match`, otherwise `False`.
    """
    pattern = re.compile(match)
    if mode == "match":
        return bool(re.match(pattern, s))
    elif mode == "search":
        return bool(re.search(pattern, s))


def filter_equals(x, match):
    """
    Determines whether x and match are equal. If x and match are both strings, match can be a regular expression.

    **Parameters**

    >*x* : `any`
    >> Any value which you want to compare against `match`.

    >*match* : `any`
    >> A reference value to compare `x` with.

    **Return** `bool`
    >> `True` if `x` and `match` are the same, otherwise `False`.
    """
    if type(x) is str and type(match) is str:
        return filter_regex(x, match, mode="match")
    else:
        return x == match


def filter_has(x,match):
    """
    Determines whether match is "in" x. If x and match are both strings, match can be a regular expression.
    **Parameters**

    >*x* : `any`
    >> A value which you want to compare against `match`.

    >*match* : `any`
    >> A reference value to compare `x` with.

    **Return** `bool`
    > `True` if `match` contains `x`, otherwise `False`.
    """
    if type(x) is str and type(match) is str:
        return filter_regex(x, match, mode="search")
    try:
        return match in x
    except TypeError:
        return False

def list_to_scd(lst):
    """
    Produces a string which joins the items of the list by semicolons. Non-string items are converted to strings
    prior to joining.

    **Parameters**

    >*lst* : `list`
    >> A list of items which are either strings or objects which can be converted to strings using `str()`

    **Return** `str`
    > A String which includes each item within `lst`, separated by semicolons.
    """
    new_lst = []
    for i in lst:
        if not isinstance(i, str):
            new_lst.append(str(i))
        else:
            new_lst.append(i)

    string = ';'.join(new_lst)

    return string

def most_common(lst, n=1):
    """
    Produces a list containing the n most common entries (occurring more than once) in a list. If the nth most common
    entry is in a tie, all these entries will be returned as well.

    **Parameters**

    >*lst* : `list`
    >> A list of values.

    >*n* : `int`
    >> A positive integer, defaulting to 1, indicating how many entries to return.

    **Return**
    > A list of tuples, each containing a frequency integer and a value.
    """
    occurrences = {}
    # Count occurrences
    for i in lst:
        if i in occurrences:
            occurrences[i] += 1
        else:
            occurrences[i] = 1

    # Remove entries with one occurrence
    s_list = []
    for j in occurrences:
        if occurrences[j] > 1:
            s_list.append((occurrences[j], j))
    s_list = sorted(s_list, reverse=True)

    # Select top n
    num_count = 1
    ret_list = []
    min = 2
    for item in s_list:
        if num_count < n:
            ret_list.append(item)
        elif num_count == n:
            ret_list.append(item)
            min = item[0]
        else:
            if item[0] == min:
                ret_list.append(item)
        num_count += 1

    return sorted(ret_list, reverse=True)

def most_occurrences(lst):
    """
    Produces the number of times the most common value appears.

    **Parameters**

    >*lst* : `list`
    >> A list of values.

    **Return** `int`
    > The number of times the most common value occurs.
    """
    occurrences = {}
    max = 0
    m_common = []
    for i in lst:
        if i in occurrences:
            occurrences[i] += 1
        else:
            occurrences[i] = 1
        if occurrences[i] > max:
            max = occurrences[i]
            m_common = [i]
        elif occurrences[i] == max:
            m_common.append(i)
    return max

# Network Edge Generator Functions
def net_edges_simple(v1, v2, record, keep):
    """
    A helper function for the Log.generate_edges() method. Creates an edge between to vertices, with an associated
    dictionary of properties.

    **Parameters**

    >*v1* : `any`
    >> The first vertex.

    >*v2* : `any`
    >> The second vertex.

    >*record* : `str`
    >> The short hash string for the current record in edge generation.

    >*keep* : `list`
    >> A list of edge attributes to be kept from the CommitLog record.

    **Record**
    > An tuple, in the format (id1, id2, {edge attribute dictionary}), representing an edge between `v1` and `v2`.
    """
    properties = {k: v for k, v in record.items() if k in keep}
    return (v1,v2, properties)


def net_edges_changes(v1, v2, record, keep):
    """
    A helper function for the Log.generate_edges() method. Creates an edge between two vertices, weighted by the number
    of lines changed. The first vertex (`v1`) can be of any type. The second vertex (`v2`) must have the type "files".

    **Parameters**

    >*v1* : `any`
    >> The first vertex.

    >*v2* : `str`
    >> A string giving the id of a vertex whose type is "files".

    >*record* : `str`
    >> The short hash string for the current record in edge generation.

    >*keep* : `list`
    >> A list of edge attributes to be kept from the CommitLog record.

    **Return**
    > A tuple, in the format (id1, id2, {edge attribute dictionary}), representing an edge between `v1` and `v2`. The
    edge attribute dictionary will contain a weight attribute, determined by the number of lines changed in `v2`.
    """
    properties = {k:v for k,v in record.items() if k in keep}
    # Get file name and change weight
    split_change = ""
    for ch in record["changes"]:
        if ch[:len(v2)+1] == v2 + " ":
            split_change = ch.split("|")
            break

    if split_change == "":
        return (v1, v2, properties)
    fname = split_change[0].replace(" ", "")
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
    return (v1, v2, properties)

# Network Attribute Helper Functions
def node_colours(d):
    """
    Produces a node's default colour, determined by whether it is an author, python file, or c file. Created to be used
    as a helper function for the MultiGraphPlus.node_attributes() method for use with a author/file bipartite network.

    **Parameters**

    >*d* : `dict`
    >> A node's attribute dictionary.

    **Return**: `str`
    > A colour string determined by the node's attributes. Nodes with a type 'author' return 'dodgerblue'. Python files
    (ending in .py) return 'tomato'. C code files (ending in .cc) return 'gold'. C interface files (ending in .h)
    return 'goldenrod'.
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

# Helpers for making UTC time strings from git time strings.

def make_utc_date(dict):
    """
    Takes an attribute dictionary. If "date" present, returns "YYYY-MM-DD" in Coordinated Universal Time.
    Otherwise, returns None. "date" must be a git-formatted string, e.g. 'Mon Apr 18 00:59:02 2016 -0400'.

    **Parameters**:

    > *dict* : `dict`

    >> An attribute dictionary.

    **Return** `string` or `none`
    """
    if "date" in dict:
        git_dt = datetime_git(dict["date"]).astimezone(dt.timezone(dt.timedelta(0)))
        return git_dt.strftime("%Y-%m-%d")
    else:
        return None

def make_utc_datetime(dict):
    """
    Takes an attribute dictionary. If "date" present, returns "YYYY-MM-DD HH:MM:SS" in
    Coordinated Universal Time. Otherwise, returns None. "date" must be a git-formatted string,
    e.g. 'Mon Apr 18 00:59:02 2016 -0400'.

    **Parameters**:

    > *dict* : `dict`

    >> An attribute dictionary.

    **Return** `string` or `none`
    """
    if "date" in dict:
        git_dt = datetime_git(dict["date"]).astimezone(dt.timezone(dt.timedelta(0)))
        return git_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return None