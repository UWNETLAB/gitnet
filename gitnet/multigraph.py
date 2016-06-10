import networkx as nx
import warnings
from gitnet.exceptions import MergeError
from gitnet.exceptions import GraphStatsError
from gitnet.helpers import list_scd_str
import matplotlib.pyplot as plt
import copy
import numpy as np
from gitnet.helpers import git_datetime
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms import bipartite


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
        This method cannot use vector attributes within the graphml file. Instead, vector attributes are converted into
            a semicolon-delimited string. When this occurs, a warning is raised indicating the vector attributes (node
            attributes are preceded by 'n:' while edge attributes are preceded by 'e:'.
        """

        graph = copy.deepcopy(self)

        warning = False
        warning_set = set([])
        for n in graph.nodes():
            for attr in graph.node[n].keys():
                if isinstance(graph.node[n][attr], list):
                    warning = True
                    warning_set = {'n:'+ attr} | warning_set
                    graph.node[n][attr] = list_scd_str(graph.node[n][attr])

        for n1, n2, data in graph.edges(data=True):
            for k in data:
                if isinstance(data[k], list):
                    warning = True
                    warning_set = {'e:'+k} | warning_set
                    data[k] = list_scd_str(data[k])

        if warning:
            warnings.warn("The provided graph contained the vector attributes: {}. All values of vector attributes have"
                          " been converted to semicolon-delimited strings. To prevent this, remove vector attributes or"
                          " convert them to atomic attributes prior to calling .write_graphml"
                          .format(warning_set))

        nx.write_graphml(graph, fpath)

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
        :return: A new MultiGraphPlus object, identical to self but with the desired attribute.
        """
        self_copy = copy.deepcopy(self)
        for n in self_copy.nodes():
            self_copy.node[n][name] = helper(self_copy.node[n])
        return self_copy

    def quickplot(self, fname, k="4/sqrt(n)", iterations=50, layout="neato", size=20, default_colour="lightgrey"):
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

    def describe(self, extra = False):
        """
        Provides a summary of graph statistics. Includes basic statistics like the number of nodes, edges,
        denstiy, and the average degree for one mode.
        Prints a string that contains each of the items that make up the summary.
        Density is calculated using one of the modes of the original bipartite network graph.

        :param extra: runs the low efficiency algorithms, which can be resource-intensive on large networks. Recommended maximum network size for the low efficiency algorithms is around 100 nodes.
        """
        mode1 = self.mode2
        mode2 = self.mode1
        density = bipartite.density(self, bipartite.sets(self)[0])
        edges = self.number_of_edges()
        nodes_mode1 = len(bipartite.sets(self)[0])
        nodes_mode2 = len(bipartite.sets(self)[1])
        if extra == True:
            # Note: for each mode of the bipartite graph, degree and betweenness centrality are the same.
            # Keeping them both makes it easy to compare them and make sure they are the same.
            degree_mode1 = bipartite.degree_centrality(self, bipartite.sets(self)[0])
            degree_mode2 = bipartite.degree_centrality(self, bipartite.sets(self)[1])
            degree_mode1 = list(degree_mode1.values())
            degree_mode2 = list(degree_mode2.values())
            degree_mode1 = np.mean(degree_mode1)
            degree_mode2 = np.mean(degree_mode2)
            betweenness_mode1 = bipartite.betweenness_centrality(self, bipartite.sets(self)[0])
            betweenness_mode1 = list(betweenness_mode1.values())
            betweenness_mode1 = np.mean(betweenness_mode1)
            betweenness_mode2 = bipartite.betweenness_centrality(self, bipartite.sets(self)[1])
            betweenness_mode2 = list(betweenness_mode2.values())
            betweenness_mode2 = np.mean(betweenness_mode2)
            G = nx.Graph(self)
            projection = bipartite.projected_graph(G, bipartite.sets(G)[0])
            transitivity = nx.transitivity(projection)
            descriptives_nodes = "This is a bipartite network of types \'" + str(mode1) + "\' and \'" + str(mode2) + "\'.\n" + str(nodes_mode1) + " nodes are of the type: \'" + str(mode1) + "\'.\n" + str(nodes_mode2) + " nodes are of the type: \'" + str(mode2) + "\'.\n"
            descriptives_edges = "There are " + str(edges) + " edges. \n"
            descriptives_density = "Density: " + str(density) + ". \n"
            descriptives_transitivity = "Transitivity: " + str(transitivity) + ". \n"
            descriptives_degree_centrality = "Mean Degree Centrality for \'" + str(mode1) + ": \'" + str(degree_mode1) + ". \nMean Degree Centrality for \'" + str(mode2) + "\': " + str(degree_mode2) + ".\n"
            descriptives_betweenness_centrality = "Mean Betweenness Centrality for " + str(mode1) + "\': " + str(betweenness_mode1) + ". \nMean Betweenness Centrality for \'" + str(mode2) + "\': " + str(betweenness_mode2) + ". \n"
            descriptives = descriptives_nodes + descriptives_edges + descriptives_density + descriptives_transitivity + descriptives_degree_centrality + descriptives_betweenness_centrality
        elif extra == False:
            descriptives_nodes = "This is a bipartite network of types \'" + str(mode1) + "\' and \'" + str(mode2) + "\'.\n" + str(nodes_mode1) + " nodes are of the type: \'" + str(mode1) + "\'.\n" + str(nodes_mode2) + " nodes are of the type: \'" + str(mode2) + "\'.\n"
            descriptives_edges = "There are " + str(edges) + " edges. \n"
            descriptives_density = "Density: " + str(density) + ". \n"
            descriptives = descriptives_nodes + descriptives_edges + descriptives_density
            print(descriptives)
            return descriptives

    def node_merge(self, node1, node2, show_warning=True):
        """
        Combines node1 and node2. After merge, node1 will remain, while node2 will be removed. node2's edges will become
            node1 edges, while retaining all their edge attributes. Vector attributes of node1 and node2 whose
            identifiers match will be combined, retaining all values. Atomic attributes which exist in only one of the
            two nodes will be included in the merge node. Finally, if node1 and node2 contain a conflicting atomic
            attribute, node1's value will overwrite node2's value.
        :param node1: The identifier for a node. This node's attributes will persist to the merged node.
        :param node2: The identifier for a second node. Any non-conflicting attributes will persist to the merged node.
        :param show_warning: A boolean parameter indicating whether overwrite warnings should be displayed
        :return: a new multigraphplus object which has merged nodes 1 and 2 together into node1, which will also have
        gained node2's edges.
        """
        merged_graph = copy.deepcopy(self)

        # Check: Both node1 and node2 exist in merged_graph
        if node1 not in merged_graph.nodes():
            raise MergeError(node1 + " is not a valid node")
        if node2 not in merged_graph.nodes():
            raise MergeError(node2 + " is not a valid node")

        # Check: node1 and node2's types are the same
        if 'type' in merged_graph.node[node1] and 'type' in merged_graph.node[node2]:
            if merged_graph.node[node1]['type'] != merged_graph.node[node2]['type']:
                raise MergeError("node1 and node2's types do not match")

        # Moves all edges from node2 to node1
        for e in merged_graph.edges(node2, data=True):
            merged_graph.add_edge(node1, e[1], attr_dict=e[2])
            merged_graph.remove_edge(e[0], e[1])

        # Adds node2's attributes to node1. There are three cases for this:
            # 1. Vector attributes are joined to create one larger vector
            # 2. Non-conflicting Atomic attributes are kept and preserved in the final node
            # 3. Conflicting Atomic attributes are not added from node2 (node1 values persist)
        node_merge_warn = False
        node_merge_warn_list = []

        for na in merged_graph.node[node2]:
            if na not in merged_graph.node[node1]:  # Deals with case 2
                merged_graph.node[node1][na] = merged_graph.node[node2][na]
            elif isinstance(merged_graph.node[node2][na], list):  # Deals with case 1
                merged_graph.node[node1][na] = merged_graph.node[node1][na] + merged_graph.node[node2][na]
            elif merged_graph.node[node1][na] != merged_graph.node[node2][na]:
                node_merge_warn = True
                node_merge_warn_list.append(na)

        merged_graph.remove_node(node2) # Removes node2

        if node_merge_warn and show_warning:
            print("Note: nodes '{}' and '{}' have the following conflicting atomic attributes: {}. In these cases, "
                  "'{}' attribute values have been retained, while '{}' values have been ignored. If you would rather "
                  "retain '{}' attributes, set '{}' to node1 and '{}' to node2."
                  .format(node1, node2, node_merge_warn_list, node1, node2, node2, node2, node1))

        return merged_graph

    def collapse_edges(self, sum_weights=False):
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
                    elif isinstance(data[k], list):
                        edge_attr[k] = data[k]
                    else:
                        edge_attr[k] = data[k]
                gnew.add_edge(n1, n2, attr_dict=edge_attr)
        return gnew
