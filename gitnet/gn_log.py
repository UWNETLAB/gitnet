import datetime as dt
import warnings

class Log(object):
    """
    Log is the basic class for the back end of gitnet. The Log class, and other classes which inherit its features,
    store all of the data retrieved by gitnet. Log has methods to describe, export, and model the data it contains.
    """

    def __init__(self,dofd = {},source = None,key_type = None):
        """
        Initializes the Log with a timestamp. Other fields default to {} or none unless otherwise specified.
        Log objects should be passed a dictionary of dictionaries after initialization, or entries should be
        added to the empty dictionary in self.collection.
        """
        self.collection = dofd
        self.timestamp = str(dt.datetime.now())
        self.source = source
        self.key_type = key_type
        # This must be updated as tags/subclasses are added. Ideally, this would be housed within each subclass.
        self.tags = self.get_tags()


    def __iter__(self):
        """
        Log iterates upon its core data set, which is a dictionary of dictionaries.
        """
        return iter(self.collection)

    def __str__(self):
        """
        A basic summary of the Log. For a more detailed report (which analyzes record contents) use the .describe method.
        """
        return "Log containing {} records from {} created at {}.".format(len(self.collection),self.source,self.timestamp)

    def __len__(self):
        """
        The number of records in self.collection.
        """
        return len(self.collection)

    def get_tags(self):
        return []

    def attributes(self):
        """
        A method for determining what data has been recorded in this commit log.
        :return: A sorted list containing every key present in the Log's records. For example, the attributes for
        a local commit log would contain hashes ("HA"), author name ("AU"), author email ("AE"), etc.
        If the self.tags attribute has been defined for this object, tags appear by their order in self.tags. Any
        unrecognized tags will be added at the end.
        """
        attr = set()
        # Add every key in the collection to a set object.
        for record in self.collection:
            attr = attr.union(self.collection[record].keys())
        # Tracking attributes
        attr_list = []
        # For every tag defined for the subclass, add to the list of attributes in order, and remove from set.
        for tag in self.tags:
            if tag in attr:
                attr.remove(tag)
                attr_list.append(tag)
        # If there are any tags left in the set (i.e. ones not specified for the subclass),
        #   add them to the end of the list (sorted).
        if len(attr) > 0:
            attr_list = attr_list + sorted(list(attr))
        return attr_list

    def describe(self):
        """
        A method which provides a description of the contents of the log.
        """
        pass

    def filter(self):
        """
        A method which filters contents based on an expression.
        (There must be online documentation of how to do this. To the Google!)
        """
        pass

    def csv(self, ignore = [], fname = None, empty_cols = False):
        """
        Converts the Log to a tab-delimited string. Note that commas aren't appropriate since commit messages
        will likely contain commas.
        """
        # Get the tags present in the Log.
        if empty_cols == True:
            types = self.tags
        else:
            types = self.attributes()
        # The number of items that were forced to strings. If > 1 at return, raise a warning.
        num_forced = 0
        # The string to be output
        out = ""
        # If a filename is given, access the file.
        if fname != None:
            f = open(fname, "w")
        # Add header line
        header = ""
        head_cur = 0
        for tag in types:
            head_cur += 1
            header = header + tag
            if head_cur != len(types):
                header = header + "\t"
            else:
                header = header + "\n"
        if fname != None:
            f.write(header)
        else:
            out = out + header
        # Create each line of output.
        for record in self.collection:
            line = ""
            tags_cur = 0
            # Add the value for each tag.
            for tag in types:
                tags_cur += 1
                # If the key is valid, add the value.
                if tag in self.collection[record].keys():
                    cur_item = self.collection[record][tag]
                    # If the item is a simple string, add it.
                    if type(cur_item) == str:
                        line = line + cur_item
                    # If the item is a list, add each string in the list.
                    elif type(cur_item) == list:
                        list_cur = 0
                        for i in cur_item:
                            list_cur += 1
                            if type(i) == str:
                                line = line + i
                            # Force a non-string to string.
                            else:
                                line = line + str(i)
                                num_forced += 1
                            if list_cur != len(cur_item):
                                line = line + ";"
                    # If the item is neither a string nor a list, force it to a string.
                    else:
                        line = line + str(cur_item)
                        num_forced += 1
                # Unless it is the last tag, add a separating tab.
                if tags_cur != len(types):
                    line = line + "\t"
            # Give the line to string or file.
            line = line + "\n"
            if fname != None:
                f.write(line)
            else:
                out = out + line
        if num_forced > 0:
            warnings.warn("Non-string input forced to string {} time(s).".format(num_forced))
        if fname != None:
            f.close()
            out = "Data written to {}".format(fname)
        return out

    def df(self,fname):
        """
        Converts the Log to a Pandas dataframe.
        See http://stackoverflow.com/questions/15455388/dict-of-dicts-of-dicts-to-dataframe.
        """
        pass

    def browse(self):
        """
        Interactively prints the contents of the Log collection, one commit at a time.
        :return: None
        """
        for key in self.collection.keys():
            print("----- {} -----".format(key))
            for rkey in self.collection[key].keys():
                print("--- {} ---".format(rkey))
                if type(self.collection[key][rkey]) == str:
                    print(self.collection[key][rkey])
                elif type(self.collection[key][rkey]) == list:
                    for s in self.collection[key][rkey]:
                        print(s)
                else:
                    warnings.warn("Dict of dict values not strings or list of strings.")
            if input("\nAnother? [press any key to continue, or press q to quit]\n") == "q":
                break



class CommitLog(Log):
    """
    A Log class for holding Git commit logs.
    """

    def get_tags(self):
        return ["HA","AU","AE","DA","MO","MG","SU","CM","CH"]

    #def __init__(self,dofd,source,key_type):
    #    super().__init__()
    #    self.tags = ["HA","AU","AE","DA","MO","MG","SU","CM","CH"]
    def ignore(self):
        """
        Not yet implemented. Mutates the CommitLog to move glob-matched change logs from the list of change logs to
        an alternate heading. This would be very useful if change log data is contaminated by non-relevant files (such
        as an automatically generated file which has many automatic changes which would otherwise be recognized as edits.)
        This will be kind of like filter (and can probably call self.filter()) but will use much more complex matching
        criteria (i.e. globs/regex).
        :return: None
        """
        pass
    pass
