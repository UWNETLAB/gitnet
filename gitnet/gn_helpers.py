import datetime

def git_datetime(s)
    """
    Turns a git date string into a datetime object.
    :param s: A git-formatted date string.
    :return: A datetime object.
    """
    return datetime.datetime.strptime(s,"%a %B %d %H:%M:%S %Y %z")

