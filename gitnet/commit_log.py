# *********************************************************************************************
# Copyright (C) 2016 Jillian Anderson, Joel Becker, Steve McColl and Dr. John McLevey
#
# This file is part of the gitnet package developed for Dr John McLevey's Networks Lab
# at the University of Waterloo. For more information, see http://networkslab.org/gitnet/.
#
# gitnet is free software: you can redistribute it and/or modify it under the terms of a
# GNU General Public License as published by the Free Software Foundation. gitnet is
# distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with gitnet.
# If not, see <http://www.gnu.org/licenses/>.
# *********************************************************************************************

import copy
import numpy as np
import warnings
import datetime
from gitnet.log import Log
from gitnet.exceptions import InputError
from gitnet.helpers import datetime_git, most_common, filter_regex, net_edges_simple, net_edges_changes


class CommitLog(Log):
    """
    A subclass of `Log` for holding git commit logs, whose data has been parsed into a dictionary of dictionaries.
    """

    def annotate(self):
        """
        A method that automatically runs after initialization. Processes date information, and adds easily parsed
        date strings to each record.

        utc_date : "YYYY-MM-DD" in Coordinated Universal Time. Formatted for `parse_date()` in `readr` package in R.
        utc_datetime : A standardized date string in Coordinated Universal Time
        """
        warnings.warn("New utc_date and utc_datetime attributes have only been tested informally.")
        for record in self:
            if "date" in self[record]:
                git_dt = datetime_git(self[record]["date"]).astimezone(datetime.timezone(datetime.timedelta(0)))
                self[record]["utc_date"] = git_dt.strftime("%Y-%m-%d")
                self[record]["utc_datetime"] = git_dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                self[record]["utc_date"] = None
                self[record]["utc_datetime"] = None

    def describe(self, mode = "default", exclude = []):
        """
        A method for creating extended descriptive output for the `Commitlog` subclass.

        **Parameters**:

        > *mode* : `string`

        >> Indicate an output mode. Currently only one implemented: "default".

        > *param* : `list`

        >> A list of output tag strings to exclude from printing. Defaults to an empty list.

        **Return** `none`

        *Output items* currently implemented (and their tag for exclusion):

        > *summary* : Prints the number of logs and creation date. Identical to `str(self)`.

        > *authors* : Prints the number of authors who commit to the repository.

        > *emails* : Prints the ten most common email address domains used by more than one user.

        > *dates* : Prints the date range for commits in the collection.

        > *changes* : Prints the mean and std. deviation of file changes, insertions, and deletions per commit.

        > *merges* : Prints the number of merges in the collection.

        > *errors* : Prints the number of parsing errors in the collection.

        """
        # Define included/excluded data summaries.
        if mode == "default":
            output = ["summary", "path", "filters", "authors", "files",
                      "emails", "dates", "changes", "merges", "errors"]
        else:
            output = ["summary", "path", "filters", "authors", "files",
                      "emails", "dates", "changes", "merges", "errors"]
        for i in exclude:
            output.remove(i)
        # Print summary
        if "summary" in output:
            print(self)
        # Print path
        if "path" in output:
            print("Origin: ", self.path)
        # Print filter summaries
        if "filters" in output:
            if len(self.filters) != 0:
                print("Filters:")
                for f in self.filters:
                    print("\t", f)
        # Print number of authors.
        if "authors" in output:
            author_dict = {}
            for record in self.collection:
                author = self.collection[record]["author"]
                if author in author_dict.keys():
                    author_dict[author] += 1
                else:
                    author_dict[author] = 1
            print("Number of authors: {}".format(len(author_dict)))
        # Print number of files.
        if "files" in output:
            num_files = len(set(self.vector("files")))
            print("Number of files: {}".format(num_files))
        # Print most common email domains.
        if "emails" in output:
            def get_domain(s):
                """
                :param s: An email address (string).
                :return: An email domain, i.e. "@domain.com" (string)
                """
                domain = s
                while True:
                    if domain == "":
                        domain = "None"
                        break
                    elif domain[0] != "@":
                        domain = domain[1:]
                    else:
                        break
                return domain
            emails = set(self.vector("email"))
            emails = list(map(get_domain, emails))
            max_domain = most_common(emails, 10)
            print("Most common email address domains:")
            for domain in max_domain:
                print("\t {} [{} users]".format(domain[1], domain[0]))
        # Print date range.
        if "dates" in output:
            early = None
            late = None
            for record in self.collection:
                date = datetime_git(self.collection[record]["date"])
                if early is None or date < early:
                    early = date
                if late is None or date > late:
                    late = date
            print("Date range: {} to {}".format(early, late))
        # Print descriptive statistics of distribution of changes (number of file edits, inserts, and deletes.)
        if "changes" in output:
            file_lst = []
            insert_lst = []
            delete_lst = []
            for record in self.collection:
                cur_record = self.collection[record]
                if "fedits" in cur_record.keys():
                    file_lst.append(cur_record["fedits"])
                if "inserts" in cur_record.keys():
                    insert_lst.append(cur_record["inserts"])
                if "deletes" in cur_record.keys():
                    delete_lst.append(cur_record["deletes"])
            print("Change distribution summary:")
            print("\t Files changed: Mean = {}, SD = {}".format(round(np.mean(file_lst), 3),
                                                                round(np.std(file_lst), 3)))
            print("\t Line insertions: Mean = {}, SD = {}".format(round(np.mean(insert_lst), 3),
                                                                  round(np.std(insert_lst), 3)))
            print("\t Line deletions: Mean = {}, SD = {}".format(round(np.mean(delete_lst), 3),
                                                                 round(np.std(delete_lst), 3)))
        # Print number of merges.
        if "merges" in output:
            n_merge = 0
            for record in self.collection:
                if "merge" in self.collection[record].keys():
                    n_merge += 1
            print("Number of merges: {}".format(n_merge))
        # Print number of parsing errors.
        if "errors" in output:
            n_errors = 0
            for record in self.collection:
                if "errors" in self.collection[record].keys():
                    n_errors += len(self.collection[record]["errors"])
            print("Number of parsing errors: {}".format(n_errors))

    def get_tags(self):
        """
        `Commitlog` tags are automatically detected by the `self.attributes()` method. Attributes are produced in the order
        specified in the get_tags method, with unexpected tags put at the end. If no tags are specified in `get_tags`,
        the attributes method will produce the tags in sorted order. The most important consequence of this ordering
        is the order of columns in TSV output.

        **Return** `list`

        > A list of ordered reference hashes.

        """
        return ["hash","author","email","date","utc_date","utc_datetime","mode","merge",
                "summary","fedits","inserts","deletes","message","files","changes"]

    def ignore(self, pattern, ignoreif="match"):
        """
        Looks for file and path names in "files" and "changes" that match (or not) a pattern (regular expression)
        and moves them into `f_ignore` and `ch_ignore` respectively. Updates `filters` attribute with ignore summary.

        **Parameters*

        > *pattern* : `string`

        >> A regular expression pattern specified by the user.

        > *ignoreif* : `string`

        >> If `matches` (default) files matching the pattern are ignored. If `no match`, files not matching pattern are ignored.

        **return**

        > A new `Commitlog` object, same as self but with the appropriate files removed.

        """
        self_copy = copy.deepcopy(self)
        for record in self_copy.collection:
            # Move files into f_ignore
            if "files" in self_copy.collection[record].keys():
                if ignoreif == "match":
                    self_copy.collection[record]["files"] = \
                        list(filter(lambda f: not(filter_regex(f, pattern, mode="search")),
                                    self_copy.collection[record]["files"]))
                elif ignoreif == "no match":
                    self_copy.collection[record]["files"] = \
                        list(filter(lambda f: filter_regex(f, pattern, mode="search"),
                                    self_copy.collection[record]["files"]))
        # Add a summary of the ignore to self_copy.filters
        ignore_note = ""
        if ignoreif == "match":
            ignore_note = "matches"
        elif ignoreif == "no match":
            ignore_note = "doesn't match"
        summary = "Ignore files that {} the regular expression: {}".format(ignore_note, pattern)
        self_copy.filters.append(summary)
        return self_copy

    def network(self, type):
        """
        A method for quickly creating preset networks using `Commitlog` data.

        **Parameters** :

        > *type* : `string`

        >> Indicates which preset to use.

        **return** :

        > A `MultiGraphPlus` object constructed with `generate_network` according to the specified defaults.

        """
        if type == "author/file/simple":
            return self.generate_network("author", "files")
        if type == "author/file":
            return self.generate_network("author", "files",
                                         edge_attributes=["author", "hash"],
                                         mode1_atom_attrs=["email"],
                                         mode2_atom_attrs=[],
                                         mode1_vector_attrs=["hash", "fedits"],
                                         mode2_vector_attrs=["date", "hash"])
        if type == "author/file/weighted":
            return self.generate_network("author", "files",
                                         edge_attributes=["author", "hash", "date"],
                                         mode1_atom_attrs=["email"],
                                         mode2_atom_attrs=[],
                                         mode1_vector_attrs=["hash", "fedits"],
                                         mode2_vector_attrs=["date", "hash"],
                                         edge_helper=net_edges_changes)
        else:
            raise InputError("{} is not a valid network preset.".format(type))

    def generate_cu_auth_changes(self):
        """
        Generates a new tag called "cu_auth_changes"; for each commit, cu_auth_changes is the cumulative changes that
        the commit's author has made to each file. The new tag is a list of strings in the format "filename:weight".
        This tag is currently not implemented as a default option (i.e. computed upon the initialization of a commit_log
        object) because it is relatively inefficient, and important only in specific types of analysis. It is of main
        concern when generating a network with edges weighted by cu_auth_changes, in which case the network generator
        will check that these weight have been computed.
        """
        warnings.warn("generate_cu_auth_changes not yet tested. Proceed with caution.")
        self_copy = copy.deepcopy(self)
        for record in self_copy:
            if "files" in self_copy[record]:
                date = self_copy[record]["date"]
                cu_log = self_copy.filter("date","before",date)
                cu_auth_log = cu_log.filter("author","equals",self_copy[record]["author"])
                cu_auth_dict = {}
                cu_auth_changes = []
                for ch in cu_auth_log.vector("changes"):
                    split_change = ch.split("|")
                    if split_change == [""]:
                        break
                    # Get the file name
                    fname = split_change[0].replace(" ", "")
                    # Get the number of changes
                    weight_str = split_change[1]
                    if "Bin" in weight_str:
                        weight = 1
                    else:
                        weight = ""
                        for char in weight_str:
                            if char.isnumeric():
                                weight += char
                        if weight == "":
                            weight = "0"
                        weight = int(weight)
                    if fname in cu_auth_dict.keys():
                        cu_auth_dict[fname] += weight
                    else:
                        cu_auth_dict[fname] = weight
                for file in self_copy[record]["files"]:
                    if file in cu_auth_dict:
                        cu_auth_changes.append("{}:{}".format(file,cu_auth_dict[file]))
                self_copy[record]["cu_auth_changes"] = cu_auth_changes
        return self_copy



