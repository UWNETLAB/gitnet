import string

# Network edge generator helper functions

def simple_edge(v1,v2):
    """

    :param v1: The first vertex, any type.
    :param v2: The second vertex, any type.
    :return:
    """
    return (v1,v2)

def fedits_edge(v1,v2):
    """

    :param v1: The first vertex, any type.
    :param v2: Must be a Git log change record string (e.g. "my_dir/my_file.txt | 5 +++--") as in CommitLog "changes"
    :return:
    """
    # Get file name and change weight
    split_change = v2.split("|")
    fname = split_change[0].replace(" ","")
    weight_str = split_change[1]
    weight = ""
    for char in weight_str:
        if char.isnumeric():
            weight += char
    if weight == "":
        weight = "0"
    return (v1,fname,int(weight))