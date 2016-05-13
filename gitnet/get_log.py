import bash as sh
import os
import warnings
from .gn_exceptions import RepositoryError, ParseError, InputError

# Example path for testing.
rp_path = "/Users/joelbecker/Documents/Work/Networks Lab/rad_pariphernalia"

def retrieve_commits(path, mode = "raw"):
    """
    retrieve_commits(path, mode = "basic") takes a file path string and a mode string and produces the  git log for the
    specified directory. The default mode, "raw" retrieves the logs by running "git log --raw". Other modes include:
    "basic" :
    retrieve_commits: Str -> Str
    Effects: If successful, prints a summary message. If unsuccesful, raises a RepositoryError.
    Example: retrieve_log("/Users/.../my_repo") => "Mode =\nbasic\ncommit df4d...\nAuthor: Socrates <socrates@gmail.com>..."
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
    identify(s) is a helper function for parse_commits(). It takes a string and attempts to identify it as an entry
    field from a Git commit log.
    identify: Str -> Str
    Example:
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



def print_dd(coll,mode="manual"):
    """
    print_dd(coll) pretty prints a dictionary of dictionaries. Requires that the values in the nested dictionaries
    are strings or lists of strings. Mode = manual to go record by record, mode = auto for entire collection.
    """
    for key in coll.keys():
        print("----- {} -----".format(key))
        for rkey in test_coll[key].keys():
            print("--- {} ---".format(rkey))
            if type(coll[key][rkey]) == str:
                print(coll[key][rkey])
            elif type(coll[key][rkey]) == list:
                for s in coll[key][rkey]:
                    print(s)
            else:
                warnings.warn("Dict of dict values not strings or list of strings.")
        if mode == "manual":
            if input("\nAnother? [press any key to continue, or press q to quit]\n") == "q":
                break



# Test
#test_coll = parse_commits(retrieve_commits(rp_path,mode="raw"))
#print_dd(test_coll,mode="manual")