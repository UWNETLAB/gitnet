import numpy as np
import copy
from gitnet.log import Log
from gitnet.exceptions import InputError
from gitnet.helpers import git_datetime, most_common, filter_regex, simple_edge, changes_edge


class CommitLog(Log):
    """
    A Log class for holding Git commit logs.
    """

    def get_tags(self):
        """
        A Log's tags are automatically detected by the self.attributes() method. Attributes are produced in the order
        specified in the get_tags method, with unexpected tags put at the end. If no tags are specified in get_tags,
        the attributes method will produce the tags in sorted order. The most important consequence of this ordering
        is the order of columns in TSV output.
        :return: A list of ordered reference hashshes.
        """
        return ["hash","author","email","date","mode","merge","summary",
                "fedits","inserts","deletes","message","files","changes"]

    def describe(self, mode = "default", exclude = []):
        """
        A method for creating an extended descriptive output for the CommitLog subclass.
        :param mode: Indicate an output mode. Currently implemented: "default"
        :param exclude: A list of output tag strings to exclude from the pringin. Default is an empty list.
        :return: None
        Output items currently implemented (and their tag for exclusion):
            - "summary" : Prints the number of logs and creation date. Identical to str(self).
            - "authors" : Prints the number of authors who commit to the repository.
            - "emails" : Prints the 10 most common email address domains used by more than one user.
            - "dates" : Prints the date range for commits in the collection.
            - "changes" : Prints the mean and std. deviation of file changes, insertions, and deletions per commit.
            - "merges" : Prints the number of merges in the collection.
            - "errors" : Prints the number of parsing errors in the collection.

        """
        # Define included/excluded data summaries.
        if mode == "default":
            output = ["summary", "path", "filters", "authors", "files",
                      "emails", "dates","changes","merges","errors"]
        else:
            output = ["summary", "path", "filters", "authors", "files",
                      "emails", "dates","changes","merges","errors"]
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
            max_domain = most_common(emails)
            print("Most common email address domains:")
            for domain in max_domain:
                print("\t {} [{} users]".format(domain[1],domain[0]))
        # Print date range.
        if "dates" in output:
            early = None
            late = None
            for record in self.collection:
                date = git_datetime(self.collection[record]["date"])
                if early == None or date < early:
                    early = date
                if late == None or late < early:
                    late = date
            print("Date range: {} to {}".format(early,late))
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
            print("\t Files changed: Mean = {}, SD = {}".format(round(np.mean(file_lst),3),
                                                                round(np.std(file_lst),3)))
            print("\t Line insertions: Mean = {}, SD = {}".format(round(np.mean(insert_lst),3),
                                                                  round(np.std(insert_lst),3)))
            print("\t Line deletions: Mean = {}, SD = {}".format(round(np.mean(delete_lst),3),
                                                                 round(np.std(delete_lst),3)))
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

    def ignore(self,pattern,ignoreif = "match"):
        """
        Looks for file/path names in "files" and "changes" that match (or does not match) pattern (a regular expression)
        and moves them into "f_ignore" and "ch_ignore" respectively. Updates "filters" attribute with ignore summary.
        :param pattern: A string/regular expression.
        :param ignoreif: If "matches" (default) files matching the pattern are ignored. If "no match", files not
        matching pattern are ignored.
        :return: A new CommitLog object, same as self but with the appropriate files removed.
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
        if ignoreif == "matches":
            ignore_note = "matches"
        elif ignoreif == "no match":
            ignore_note = "doesn't match"
        summary = "Ignore files that {} the regular expression: {}".format(ignore_note,pattern)
        self_copy.filters.append(summary)
        return self_copy

    def network(self, type):
        """
        A method for quickly creating preset networks using CommitLog data.
        :param type: A string indicating which preset to use.
        :return: A MultiGraphPlus object constructed with generate_network according to the specified defaults.
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
                                         edge_helper=changes_edge)
        else:
            raise InputError("{} is not a valid network preset.".format(type))