import networkx as nx
import warnings
import matplotlib.pyplot as plt


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
        if warning:
            warnings.warn("The provided graph contained the vector attributes: {}. All values of vector attributes have"
                          " been converted to 'None'. To prevent this, remove vector attributes or convert them to "
                          "atomic attributes prior to calling .write_graphml"
                          .format(warning_list))

    def node_attributes(self,name,helper):
        """
        Creates a new node attribute.
        :param name: The name of the new attribute.
        :param helper: A helper function, which takes an attribute dict and produces the new attribute.
        :return: None
        """
        for n in self.nodes():
            self.node[n][name] = helper(self.node[n])

    def quickplot(self, layout = "spring", fname = None, size = 10):
        colour_data = {}
        for n in self.nodes():
            if "colour" in self.node[n].keys():
                colour_data[n] = self.node[n]["colour"]
            elif "color" in self.node[n].keys():
                colour_data[n] = self.node[n]["color"]
            else:
                colour_data[n] = "lightgrey"
        colour_list = [colour_data[node] for node in self.nodes()]
        if layout == "spring":
            nx.draw_spring(self,
                            node_size = size,
                            font_size = 5,
                            node_color =colour_list,
                            linewidths = .5,
                            edge_color = "DarkGray",
                            width = .1,
                            k = .01,
                            iterations=100)
        elif layout == "circular":
            nx.draw_circular(self,
                            node_size = size,
                            font_size = 5,
                            node_color =colour_list,
                            linewidths = .5,
                            edge_color = "DarkGray",
                            width = .1,
                            k = 1000)
        elif layout == "shell":
            nx.draw_shell(self,
                           node_size=size,
                           font_size=5,
                           node_color =colour_list,
                           linewidths=.5,
                           edge_color="DarkGray",
                           width=.1,
                           k=1000)
        elif layout == "spectral":
            nx.draw_spectral(self,
                           node_size=size,
                           font_size=5,
                           node_color =colour_list,
                           linewidths=.5,
                           edge_color="DarkGray",
                           width=.1,
                           k=1000)
        elif layout == "random":
            nx.draw_random(self,
                           node_size=size,
                           font_size=5,
                           node_color =colour_list,
                           linewidths=.5,
                           edge_color="DarkGray",
                           width=.1,
                           k=1000)
        if fname is not None:
            plt.savefig(fname)
            print("Wrote file: {}".format(fname))

    def node_merge(self, node1, node2):
        """
        Combines node1 and node2, retaining all the node attributes of node1.
        :param node1:
        :param node2:
        :return:
        """
        #TODO: 3 situations for n attr: 1 Lists (append) 2 Non-conflicting atomic(add) 3. Conflicting atomic (overwrite)
        #TODO: retain edge attributes
        for e in self.edges(node2):
            self.add_edge(node1, e[1])
            self.remove_edge(e[0], e[1])
