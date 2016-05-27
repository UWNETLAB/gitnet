import re

# Network edge generator helper functions

def simple_edge(v1, v2, record, keep):
    """
    Creates an edge between to vertices, with an associated dictionary of properties.
    :param v1: The first vertex, any type.
    :param v2: The second vertex, any type.
    :return:
    """
    properties = {k:v for k,v in record.items() if k in keep}
    return (v1,v2, properties)

# TODO: changes_edge is currently broken. Fix it. Make it work taking in "file" but still getting lines changed
def changes_edge(v1, v2, record, keep):
    """
    Creates an edge between an "any" and a CommitLog file ("file"), weighted by the number of lines changed
    in the file.
    :param v1: The first vertex, any type.
    :param v2: Must be a file string (e.g. "my_dir/my_file.txt") as in CommitLog "files"
    :return:
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
    weight_str = record["changes"][1]
    weight = ""
    for char in weight_str:
        if char.isnumeric():
            weight += char
    if weight == "":
        weight = "0"
    properties["weight"] = int(weight)
    return (v1,v2,properties)