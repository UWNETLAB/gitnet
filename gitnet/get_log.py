import bash as sh
import os
import warnings
from gitnet.gn_exceptions import RepositoryError, ParseError, InputError
from gitnet.gn_log import CommitLog



def retrieve_commits(path, mode = "stat"):
    """
    retrieve_commits takes a file path string and a mode string and produces the  git log for the
    specified directory. The default mode, "stat" retrieves the logs by running "git log --stat". Modes include:
    "basic" ("git log"), "raw" ("git log --raw"), and "stat" ("git log --stat").
    :param path: A string identifying the path to the target git repository.
    :param mode: A string identifying the git log mode to be retrieved. Default mode is "stat".
    :return: Returns a large string containing the raw output from the repository's git log.
    """
    print("Attempting local git log retrieval...")
    # Log command modes, referenced by "mode" input.
    log_commands = {"basic": "git log", "raw": "git log --raw", "stat":"git log --stat"}
    if mode not in log_commands.keys():
        raise InputError("{} is not a valid retrieval mode.".format(mode))
    # Save the current directory. Navigate to new directory. Retrieve logs. Return to original directory.
    work_dir = os.getcwd()
    os.chdir(path)
    raw_logs = str(sh.bash(log_commands[mode]).stdout)[2:-1].replace("\\n","\n").replace("\\t","\t")
    os.chdir(work_dir)
    # If the retrieval was unsuccessful, raise an error.
    if len(raw_logs) == 0:
        print("Raising error.")
        if "true" in str(sh.bash("git rev-parse --is-inside-work-tree").stdout):
            raise RepositoryError("The specified directory is not a Git repository.")
        else:
            raise RepositoryError("This Git repository has no commits.")
    # If the retrieval was successful, print a summary."
    print("Got {} characters from: {}".format(len(raw_logs), path))
    # Record the retrieval mode.
    raw_logs = "Mode =\n{}\n".format(mode) + raw_logs
    return raw_logs



def identify(s):
    """
    identify is a helper function for parse_commits(). It takes a string and attempts to identify it as an entry
    field from a Git commit log.
    :param s: A string. One line of standard git log output (in basic, raw, or stat mode.)
    :return: A string identifying the type of data received.

    Examples:
    identify("commit 5be676481b4051af62f21eb2c8601b3f6bafb195") => "hash"
    identify("Author: JBWBecker <joelbecker@gto.net>") => "author"
    identify("__init__.py                                  |   2 ++") => "change"
    """
    # identify checks whether the string matches an expected format. All matches are saved in a list.
    matches = []
    if "commit" in s and len(s) == 47:
        matches.append("hash")
    if s[:7] == "Author:":
        matches.append("author")
    if s[:5] == "Date:":
        matches.append("date")
    if s[:4] == "    ":
        matches.append("message")
    if (s[0] == " " and s[:5] != "    " and "|" in s) or (s[0] == ":" and type(int(s[1:8])) == int):
        matches.append("change")
    if s[0] == " " and s[:5] != "    " and (("insertion" in s and "(+)" in s) or ("deletion" in s and "(-)" in s)):
        matches.append("summary")
    if s[:6] == "Merge:":
        matches.append("merge")
    # If only one match was found, produce that string. Otherwise, produce "other" and raise a Warning.
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        warnings.warn("Unexpected parsing behaviour. <{}> matched multiple input patterns during parsing,"
                      " so was identified as 'other'.".format(s))
        return "multiple"
    else:
        warnings.warn("Unexpected parsing behaviour. <{}> did not match any input patterns during parsing,"
                      " so was identified as 'other'.".format(s))
        return "none"



def parse_commits(commit_str):
    """
    Parses a raw string containing a commit Log for a Git repository. It produces a dictionary
    of dictionaries keyed by an abbreviated commit hash, containing a series of data points indexed by short reference
    codes.
    :param commit_str: Raw commit log data, as produced by retreive_commits. Modes currently supported: Basic, Raw, Stat.
    :return: A dictionary of dictionaries keyed by an abbreviated commit hash. Each sub-dictionary contains a dictionary
    recording the data from one commit log.

    Git log data types currently implemented: hash ("HA"), mode ("MO"), author name ("AU"), author email ("AE"),
    date ("DA"), commit message ("CM"), merge ("MG"), summary ("SU"), and a list of change records ("CH").

    Error data types currently implemented (with warnings): multiple patterns matched during parse ("ER"), no patterns
    matched during parse ("ER").
    """
    # Split and clean retrieved logs, creating a list of strings and removing empty strings.
    commit_list = list(filter(lambda s: s != "",commit_str.split("\n")))
    mode_list = ["basic","raw","stat"]
    # Get the mode signature and the mode string.
    mode_sig = commit_list.pop(0)
    mode = commit_list.pop(0)
    if mode_sig != "Mode =":
        raise ParseError("Invalid input. parse_commits() expected a string beginning with 'Mode =\n'. See documentation.")
    if mode not in mode_list:
        raise ParseError("Invalid input. {} is not a valid mode.".format(mode))
    # Initialize a dictionary to store processed records, and a temporary short hash tracker, which tracks current commit.
    collection = {}
    sha = ""
    # Iterate through list of input lines. Process lines according to type using the identify() helper function.
    for line in commit_list:
        id = identify(line)
        # Commit Hash?
        if id == "hash":
            sha = line[7:14]
            collection[sha] = {}
            collection[sha]["HA"] = line[7:]
            collection[sha]["MO"] = mode
        # Author?
        elif id == "author":
            collection[sha]["AU"] = line.split("<")[0][8:-1]
            collection[sha]["AE"] = line.split("<")[1][:-1]
        # Date?
        elif id == "date":
            collection[sha]["DA"] = line[8:]
        # Message?
        elif id == "message":
            if "CM" in collection[sha].keys():
                collection[sha]["CM"] += " " + line[4:]
            else:
                collection[sha]["CM"] = line[4:]
        # File change record?
        elif id == "change":
            if "CH" in collection[sha].keys():
                collection[sha]["CH"].append(line[1:])
            else:
                collection[sha]["CH"] = [line[1:]]
        elif id == "summary":
            collection[sha]["SU"] = line[1:]
        elif id == "merge":
            collection[sha]["MG"] = line[6:]
        elif id == "multiple" or id == "none":
            if "ER" in collection[sha].keys():
                collection[sha]["ER"].append(line)
            else:
                collection[sha]["ER"] = [line]
        else:
            warnings.warn("Parser was unable to identify {}. Identity string <{}> not recognized".format(line,id))
    return collection




def get_log(path,mode = "stat",commit_source = "local git"):
    """
    A function for gathering data from a local Git repository.
    :param path: A string containing the path of the Git repository.
    :param mode: The retrieval mode. Modes currently implemented: "basic", "raw", "stat".
    :return: A CommitLog object.
    """
    if commit_source == "local git":
        detect_key = "hash"
    else:
        detect_key = "unknown"
    return CommitLog(dofd = parse_commits(retrieve_commits(path,mode)),
                     source = commit_source,
                     key_type = detect_key)
