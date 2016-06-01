import networkx as nx
import matplotlib.pyplot as plt

class MultiGraphPlus(nx.MultiGraph):

    def write_graphml(self, fpath):
        """
        :param self: MultiGraphPlus graph
        :param fpath: A string indicating the path or file name to write. File names which end in .gz or .bz2 will be compressed.
        :return:
        """
        nx.write_graphml(self, fpath)

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