import networkx as nx
import warnings
import matplotlib.pyplot as plt
import copy
import numpy as np
from gitnet.gn_helpers import git_datetime
from networkx.drawing.nx_agraph import graphviz_layout


class MultiGraphPlus(nx.MultiGraph):

    mode1 = ""

    mode2 = ""

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

    def write_tnet(self, fname, mode_string="type", weighted=False, time_string="date", node_index_string="tnet_id",
                   weight_string='weight'):
        """
        A function to write an edgelist formatted for the tnet library for network analysis in R.
        :param fname: The name of the tnet file to be created.
        :param mode_string: The name string of the mode node attribute.
        :param weighted: Do the edges have weights? True or false.
        :param time_string: the name string of the date/time node attribute.
        :param node_index_string: Creates a new integer id attribute.
        :param weight_string: The name of the weight node attribute.
        :return: None

        Source: Adapted from code written by Reid McIlroy Young for the Metaknowledge python library.
        """
        modes = []
        mode1Set = set()
        for node_index, node in enumerate(self.nodes_iter(data=True), start=1):
            try:
                nMode = node[1][mode_string]
            except KeyError:
                # too many modes so will fail
                modes = [1, 2, 3]
                nMode = 4
            if nMode not in modes:
                if len(modes) < 2:
                    modes.append(nMode)
                else:
                    raise ValueError(
                        "Too many modes of '{}' found in the network or one of the nodes was missing its mode. There must be exactly 2 modes.".format(
                            mode_string))
            if nMode == modes[0]:
                mode1Set.add(node[0])
            node[1][node_index_string] = node_index
        if len(modes) != 2:
            raise ValueError(
                "Too few modes of '{}' found in the network. There must be exactly 2 modes.".format(mode_string))
        with open(fname, 'w', encoding='utf-8') as f:
            for n1, n2, eDict in self.edges_iter(data=True):
                if n1 in mode1Set:
                    if n2 in mode1Set:
                        raise ValueError(
                            "The nodes '{}' and '{}' have an edge and the same type. The network must be purely 2-mode.".format(
                                n1, n2))
                elif n2 in mode1Set:
                    n1, n2 = n2, n1
                else:
                    raise ValueError(
                        "The nodes '{}' and '{}' have an edge and the same type. The network must be purely 2-mode.".format(
                            n1, n2))
                if time_string is not None and time_string in eDict:
                    edt = eDict[time_string]
                    if type(edt) is str:
                        edt = git_datetime(eDict[time_string])
                    e_time_string = edt.strftime("\"%y-%m-%d %H:%M:%S\"")
                else:
                    e_time_string = ''
                # Write to file
                node1 = self.node[n1][node_index_string]
                node2 = self.node[n2][node_index_string]
                weight = eDict[weight_string]
                if time_string != None:
                    f.write("{} {} {}".format(e_time_string,node1,node2))
                else:
                    f.write("{} {}".format(node1,node2))
                if weighted:
                    f.write(" {}\n".format(weight))
                else:
                    f.write("\n")


    def node_attributes(self,name,helper):
        """
        Creates a new node attribute.
        :param name: The name of the new attribute.
        :param helper: A helper function, which takes an attribute dict and produces the new attribute.
        :return: None
        """
        for n in self.nodes():
            self.node[n][name] = helper(self.node[n])

    def quickplot(self, fname, k = "4/sqrt(n)", iterations = 50, layout = "neato", size = 20, default_colour = "lightgrey"):
        """
        Makes a quick visualization of the network.
        :param layout: The type of layout to draw. ("spring", "circular", "shell", "spectral", or "random")
        :param fname: If specified, a copy of the figure is saved using this file name.
        :param size: The size of the nodes. Default is 20.
        :return: None
        """
        if type(k) is str:
            k = 4/np.sqrt(self.number_of_nodes())
        # Make a copy
        copy_net = copy.deepcopy(self)
        # Remove isolates
        copy_net.remove_nodes_from(nx.isolates(copy_net))
        # Add detect colour attribute
        colour_data = {}
        for n in copy_net.nodes():
            if "colour" in copy_net.node[n].keys():
                colour_data[n] = copy_net.node[n]["colour"]
            elif "color" in copy_net.node[n].keys():
                colour_data[n] = copy_net.node[n]["color"]
            else:
                colour_data[n] = default_colour
        colour_list = [colour_data[node] for node in copy_net.nodes()]
        # Plot the network
        print("Plotting...")
        if layout in ["dot", "neato", "fdp", "circo"]:
            nx.draw(copy_net,
                    pos = graphviz_layout(copy_net,prog=layout),
                    node_size = size,
                    font_size = 5,
                    node_color = colour_list,
                    linewidths = .5,
                    edge_color = "DarkGray",
                    width = .1)
        if layout == "spring":
            nx.draw(copy_net,
                    pos=nx.spring_layout(copy_net,k=k,iterations=iterations),
                    node_size=size,
                    font_size=5,
                    node_color=colour_list,
                    linewidths=.5,
                    edge_color="DarkGray",
                    width=.1)
        elif layout == "circular":
            nx.draw_circular(copy_net,
                            node_size = size,
                            font_size = 5,
                            node_color =colour_list,
                            linewidths = .5,
                            edge_color = "DarkGray",
                            width = .1)
        elif layout == "shell":
            nx.draw_shell(copy_net,
                           node_size=size,
                           font_size=5,
                           node_color =colour_list,
                           linewidths=.5,
                           edge_color="DarkGray",
                           width=.1)
        elif layout == "spectral":
            nx.draw_spectral(copy_net,
                           node_size=size,
                           font_size=5,
                           node_color =colour_list,
                           linewidths=.5,
                           edge_color="DarkGray",
                           width=.1)
        elif layout == "random":
            nx.draw_random(copy_net,
                           node_size=size,
                           font_size=5,
                           node_color =colour_list,
                           linewidths=.5,
                           edge_color="DarkGray",
                           width=.1)
        # Save figure if applicable
        if fname is not None:
            plt.savefig(fname,bbox_inches="tight")
            print("Wrote file: {}".format(fname))

    def describe(self):
        print("A MultiGraphPlus object with {} nodes and {} edges.".format(len(self.nodes()), len(self.edges())))

    def node_merge(self, node1, node2):
        """
        Combines node1 and node2. After merge, node1 will remain, while node2 will be removed. node2's edges will become
            node1 edges, while retaining all their edge attributes. Vector attributes of node1 and node2 whose
            identifiers match will be combined, retaining all values. Atomic attributes which exist in only one of the
            two nodes will be included in the merge node. Finally, if node1 and node2 contain a conflicting atomic
            attribute, node1's value will overwrite node2's value.
        :param node1: The identifier for a node. This node's attributes will persist to the merged node.
        :param node2: The identifier for a second node. Any non-conflicting attributes will persist to the merged node.
        :return: a new multigraphplus object which has merged nodes 1 and 2 together into node1, which will also have
        gained node2's edges.
        """
        merged_graph = copy.deepcopy(self)

        # Moves all edges from node2 to node1
        print('Merging edges...')
        for e in merged_graph.edges(node2, data=True):
            merged_graph.add_edge(node1, e[1], attr_dict=e[2])
            merged_graph.remove_edge(e[0], e[1])
        # Adds node2's attributes to node1. There are three cases for this:
            # 1. Vector attributes are joined to create one larger vector
            # 2. Non-conflicting Atomic attributes are kept and preserved in the final node
            # 3. Conflicting Atomic attributes are not added from node2 (node1 values persist)
        node_merge_warn = False
        node_merge_warn_list = []
        print('Merging nodes...')
        for na in merged_graph.node[node2]:
            if na not in merged_graph.node[node1]:  # Deals with case 2
                merged_graph.node[node1][na] = merged_graph.node[node2][na]
            elif isinstance(merged_graph.node[node2][na], list):  # Deals with case 1
                merged_graph.node[node1][na] = merged_graph.node[node1][na] + merged_graph.node[node2][na]
            elif merged_graph.node[node1][na] != merged_graph.node[node2][na]:
                node_merge_warn = True
                node_merge_warn_list.append(na)
        merged_graph.remove_node(node2) # Removes node2
        if node_merge_warn:
            print("Note: nodes '{}' and '{}' have the following conflicting atomic attributes: {}. In these cases, "
                  "'{}' attribute values have been retained, while '{}' values have been ignored. If you would rather "
                  "retain '{}' attributes, set '{}' to node1 and '{}' to node2.\n"
                  .format(node1, node2, node_merge_warn_list, node1, node2, node2, node2, node1))
        return merged_graph

    def collapse_edges(self, sum_weights = False):
        """
        Collapses all edges which share nodes into one edge, with a new weight assigned to it. How this weight is
        assigned depends on the sum_weights parameter.

        :param sum_weights: An optional boolean parameter. Determines how weights will be assigned to the final edges. If
        False, the weight will be the number of edges which were collapsed. If True, the weight will be the sum of the
        weights of collapsed edges.

        :return: A new MultiGraphPlus object, which has collapsed all duplicate edges, assigned a new weight, and
        stores other edge data in lists.

        Note: The default weight of an edge is 1. Thus, if sum_weights is set to True, but an edge does not have a
        weight attribute, this method assumes the weight of the edge is 1.

        """
        gnew = MultiGraphPlus()
        for n1, n2, data in self.edges(data=True):
            if gnew.has_edge(n1,n2):
                gnew_data = gnew.edge[n1][n2][0]
                if 'weight' not in data:
                    gnew_data['weight'] += 1
                for k in data:
                    if k in gnew_data:
                        if k == 'weight':
                            if sum_weights:
                                gnew_data[k] += data[k]
                            else:
                                gnew_data[k] += 1
                        elif isinstance(data[k], list):
                            gnew_data[k] += data[k]
                        else:
                            if isinstance(gnew_data[k], list):
                                gnew_data[k] += [data[k]]
                            else:
                                gnew_data[k] = [gnew_data[k], data[k]]
                    else:
                        gnew_data[k] = data[k]
            else:
                edge_attr = {'weight': 1}
                for k in data:
                    if k == 'weight':
                        if sum_weights:
                            edge_attr[k] = data[k]
                        else:
                            pass
                    elif isinstance(data[k], list):
                        edge_attr[k] = data[k]
                    else:
                        edge_attr[k] = data[k]
                gnew.add_edge(n1, n2, attr_dict=edge_attr)
        return gnew
