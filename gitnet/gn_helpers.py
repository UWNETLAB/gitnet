import datetime

def git_datetime(s):
    """
    Turns a git date string into a datetime object.
    :param s: A git-formatted date string.
    :return: A datetime object.
    """
    return datetime.datetime.strptime(s,"%a %b %d %H:%M:%S %Y %z")

def most_common(lst):
    """
    Produces a list containing the most common entry in a list (more than one entry if there is a tie.)
    :param lst: A list of values.
    :return: A list of the most common values.
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
    return m_common

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