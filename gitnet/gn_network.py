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

def fedits_edge(v1, v2, record, keep):
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
    properties = {k:v for k,v in record.items() if k in keep}
    properties["weight"] = int(weight)
    return (v1,fname,properties)