import bash as sh
import os
from gn_exceptions import RepositoryError, ParseError

os.chdir("/Users/joelbecker/Documents/School")

def temp(mode):
    if mode == "dir":
        print(os.getcwd())

# Example path for testing.
rp_path = "/Users/joelbecker/Documents/Work/Networks Lab/rad_pariphernalia"




def retrieve_commits(path, mode = "basic"):
    """
    retrieve_commits(path, mode = "basic") takes a file path string and a mode string and produces the  git log for the
    specified directory. The default mode, "basic" retrieves the logs by running "git log".
    retrieve_commits: Str -> Str
    Effects: If successful, prints a summary message. If unsuccesful, raises a RepositoryError.
    Example: retrieve_log("/Users/.../my_repo") => "Mode =\\nbasic\\ncommit df4d...\\nAuthor: Socrates <socrates@gmail.com>..."
    """
    # Set retrieval mode.
    log_command = "git log"
    if mode == "basic":
        pass
    # Save the current directory. Navigate to new directory. Retrieve logs. Return to original directory.
    work_dir = os.getcwd()
    os.chdir(path)
    raw_logs = str(sh.bash(log_command).stdout)[2:-1]
    os.chdir(work_dir)
    # If the retrieval was unsuccessful, raise an error.
    if len(raw_logs) == 0:
        if "true" in str(sh.bash("git rev-parse --is-inside-work-tree").stdout):
            raise RepositoryError("The specified directory is not a Git repository.")
        else:
            raise RepositoryError("This Git repository has no commits.")
    # If the retrieval was successful, print a summary."
    print("Got {} characters from: {}".format(len(raw_logs), path))
    # Record the retrieval mode.
    raw_logs = "Mode =\\n{}\\n".format(mode) + raw_logs
    return raw_logs

# Testing. Seems to work for another directory. Needs error handling.
def test1(go = False):
    if go:
        print(retrieve_commits(rp_path))
        print(retrieve_commits("/Users/joelbecker/Documents/School"))

def parse_commits(commit_str):
    # Split and clean retrieved logs.
    commit_list = list(filter(lambda s: s != "",commit_str.split("\\n")))
    mode_list = ["basic"]
    mode_sig = commit_list.pop(0)
    mode = commit_list.pop(0)
    if mode_sig != "Mode =":
        raise ParseError("Invalid input. parse_commits() expected a string beginning with 'Mode =\\n'. See documentation.")
    if mode not in mode_list:
        raise ParseError("Invalid input. {} is not a valid mode.".format(mode))
    collection = {}
    # Parse git log in basic mode.
    if mode == "basic":

