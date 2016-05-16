import datetime as dt

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

    def attributes(self):
        """
        Returns a set object containing every key present in the Log's records. For example, the attributes for
        a local commit log would contain hashes ("HA"), author name ("AU"), author email ("AE"), etc.
        """
        attr = set()
        for record in self.collection:
            attr = attr.union(self.collection[record].keys())
        return attr

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

    def csv(self, fname):
        """
        Converts the Log to a CSV formatted string.
        """
        pass

    def df(self,fname):
        """
        Converts the Log to a Pandas dataframe.
        """
        pass



class CommitLog(Log):
    """
    A Log class for holding Git commit logs.
    """
    pass
