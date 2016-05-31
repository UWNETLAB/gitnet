import networkx as nx
import warnings


class MultiGraphPlus(nx.MultiGraph):
    def write_graphml(self, fpath):
        """
        write_graphml converts a MultiGraphPlus object to a graphml file.
        :param self: MultiGraphPlus graph
        :param fpath: A string indicating the path or file name to write. File names which end in .gz or .bz2 will be compressed.
        :return: None
        This method will have the side effect of creating a file, specified by fpath.
        This method cannot use vector attributes within the graphml file. Instead, it replaces the attribute values with
            the dummy value 'None'. When this occurs, a warning is raised indicating the vector attributes in self.
        """
        warning = False
        warning_list = set([])
        for n in self.nodes():
            for attr in self.node[n].keys():
                if isinstance(self.node[n][attr], list):
                    warning = True
                    warning_list = set([attr]) | warning_list
                    self.node[n][attr] = 'None'

        nx.write_graphml(self, fpath)
        warnings.warn("The provided graph contained the vector attributes: {}. All values of vector attributes have "
                      "been converted to 'None'. To prevent this, remove vector attributes or convert them to atomic "
                      "attributes prior to calling .write_graphml"
                      .format(warning_list))
