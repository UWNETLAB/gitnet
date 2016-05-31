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

