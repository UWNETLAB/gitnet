class gitnetException(Exception):
    pass


class RepositoryError(gitnetException):
    """
    Exception given when a problem is detected when interacting with a Git repository.
    """
    pass


class ParseError(gitnetException):
    """
    Exception given when an error occurs duing parsing.
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
