# Written by Jillain Anderson, Joel Becker, and Steve McColl for Dr. John McLevey's Networks Lab, University of Waterloo, 2016.
# Permissive free software license - BSD/MIT.
class gitnetException(Exception):
    pass


class RepositoryError(gitnetException):
    """
    Exception given when a problem is detected when interacting with a Git repository.
    """
    pass


class ParseError(gitnetException):
    """
    Exception given when an error occurs during parsing.
    """
    pass


class InputError(gitnetException):
    """
    Exception given when the user gives an invalid input.
    """
    pass


class NetworkError(gitnetException):
    """
    Exception given when there is a problem converting a Log Object to a MultiGraphPlus Object.
    """


class ExportError(gitnetException):
    """
    Exception given when gitnet is unable to export a given edgelist, node attribute list, or other object.
    """


class MergeError(gitnetException):
    """
    Exception given when the user provides nodes to node_merge() which do not meet the initial checks
    """
    pass

class GraphStatsError(gitnetException):
    """
    Exception given when the statistics are not generated as expected.
    """
    pass
