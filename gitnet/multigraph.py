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

import networkx as nx
import os
import warnings
from gitnet.exceptions import MergeError
from gitnet.helpers import list_to_scd
import matplotlib.pyplot as plt
import copy
import numpy as np
from gitnet.helpers import datetime_git
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms import bipartite


class MultiGraphPlus(nx.MultiGraph):

    mode1 = ""

    mode2 = ""

    def write_graphml(self, fname):
        """
        Converts a `MultiGraphPlus` object to a graphml file.

        **Parameters** :

        > *fname* :

        >> A string indicating the path or file name to write to. File names which end in `.gz` or `.bz2` will be compressed.

        **Return** : `None`

        > This method will have the side effect of creating a file, specified by fpath.
        > This method cannot use vector attributes within the graphml file. Instead, vector attributes are converted into
        > a semicolon-delimited string. When this occurs, a warning is raised indicating the vector attributes (node
        > attributes are preceded by 'n:' while edge attributes are preceded by 'e:').

        """

        graph = copy.deepcopy(self)

        warning = False
        warning_set = set([])
        for n in graph.nodes():
            for attr in graph.node[n].keys():
                if isinstance(graph.node[n][attr], list):
                    warning = True
                    warning_set = {'n:' + attr} | warning_set
                    graph.node[n][attr] = list_to_scd(graph.node[n][attr])

        for n1, n2, data in graph.edges(data=True):
            for k in data:
                if isinstance(data[k], list):
                    warning = True
                    warning_set = {'e:'+k} | warning_set
                    data[k] = list_to_scd(data[k])

        if warning:
            warnings.warn("The provided graph contained the vector attributes: {}. All values of vector attributes have"
                          " been converted to semicolon-delimited strings. To prevent this, remove vector attributes or"
                          " convert them to atomic attributes prior to calling .write_graphml"
                          .format(warning_set))
        nx.write_graphml(graph, fname)
        print("Success. Wrote GraphML file {} to {}".format(fname, os.getcwd()))

    def write_tnet(self, fname, mode_string="type", weighted=False, time_string="date", node_index_string="tnet_id",
                   weight_string='weight'):
        """
        A function to write an edgelist formatted for the tnet library for network analysis in R.

        **Parameters** :

        > *fname* : `string`

        >> A string indicating the path or file name to write to.

        > *mode_string* : `string`

        >> The name string of the mode node attribute.

        > *weighted* : `bool`

        >> Do the edges have weights? True or false.

        > *time_string* : `string`

        >> the name string of the date/time node attribute.

        > *node_index_string* : `int`

        >> Creates a new integer id attribute.

        > *weight_string* : `string`

        >> The name of the weight node attribute.

        **Return** : `None`

        *Source* :

        > Adapted from code written by Reid McIlroy Young for the Metaknowledge python library.

        """
        modes = []
        mode1set = set()
        for node_index, node in enumerate(self.nodes_iter(data=True), start=1):
            try:
                nmode = node[1][mode_string]
            except KeyError:
                # too many modes so will fail
                modes = [1, 2, 3]
                nmode = 4
            if nmode not in modes:
                if len(modes) < 2:
                    modes.append(nmode)
                else:
                    raise ValueError(
                        "Too many modes of '{}' found in the network or one of the nodes was missing its mode. "
                        "There must be exactly 2 modes.".format(mode_string))
            if nmode == modes[0]:
                mode1set.add(node[0])
            node[1][node_index_string] = node_index
        if len(modes) != 2:
            raise ValueError(
                "Too few modes of '{}' found in the network. There must be exactly 2 modes.".format(mode_string))
        with open(fname, 'w', encoding='utf-8') as f:
            for n1, n2, eDict in self.edges_iter(data=True):
                if n1 in mode1set:
                    if n2 in mode1set:
                        raise ValueError(
                            "The nodes '{}' and '{}' have an edge and the same type. "
                            "The network must be purely 2-mode.".format(n1, n2))
                elif n2 in mode1set:
                    n1, n2 = n2, n1
                else:
                    raise ValueError(
                        "The nodes '{}' and '{}' have an edge and the same type. "
                        "The network must be purely 2-mode.".format(n1, n2))

                if time_string is not None and time_string in eDict:
                    edt = eDict[time_string]
                    if type(edt) is str:
                        edt = datetime_git(eDict[time_string])
                    e_time_string = edt.strftime("\"%y-%m-%d %H:%M:%S\"")
                else:
                    e_time_string = ''

                # Write to file
                node1 = self.node[n1][node_index_string]
                node2 = self.node[n2][node_index_string]
                if time_string is not None:
                    f.write("{} {} {}".format(e_time_string, node1, node2))
                else:
                    f.write("{} {}".format(node1, node2))

                if weighted:
                    weight = eDict[weight_string]
                    f.write(" {}\n".format(weight))
                else:
                    f.write("\n")
        print("Success. Wrote Tnet file {} to {}".format(fname, os.getcwd()))

    def node_attributes(self, name, helper):
        """
        Creates a new node attribute.

        **Parameters** :

        > *name* : `string`

        >> The name of the new attribute.

        > *helper* : `None`

        >> A helper function, which takes an attribute dict and produces the new attribute.

        **Return** :

        > A new MultiGraphPlus object, identical to self but with the desired attribute.

        """
        self_copy = copy.deepcopy(self)
        for n in self_copy.nodes():
            self_copy.node[n][name] = helper(self_copy.node[n])
        return self_copy

    def quickplot(self, fname, k="4/sqrt(n)", iterations=50, layout="neato", size=20, default_colour="lightgrey"):
        """
        Makes a quick visualization of the network.

        **Parameters** :

        > *fname* : `string`

        >> A string indicating the path or file name to write to.

        > *k* : `None`

        >> Default function used for plotting.

        > *iterations* : `int`

        >> Default number of iterations to run on the plot.

        > *layout* : `string`

        >> The type of layout to draw, the available layouts are: ("spring", "circular", "shell", "spectral", or "random").

        > *size* : `int`

        >> The size of the nodes. Default is 20.

        > *default_colour* : `string`

        >> Only default nodes will be coloured with this colour.

        **Return** : `None`

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
                pos=graphviz_layout(copy_net, prog=layout),
                node_size=size,
                font_size=5,
                node_color=colour_list,
                linewidths=.5,
                edge_color="DarkGray",
                width=.1)
        if layout == "spring":
            nx.draw(copy_net,
                pos=nx.spring_layout(copy_net, k=k, iterations=iterations),
                node_size=size,
                font_size=5,
                node_color=colour_list,
                linewidths=.5,
                edge_color="DarkGray",
                width=.1)
        elif layout == "circular":
            nx.draw_circular(copy_net,
                node_size=size,
                font_size=5,
                node_color=colour_list,
                linewidths=.5,
                edge_color="DarkGray",
                width=.1)
        elif layout == "shell":
            nx.draw_shell(copy_net,
                node_size=size,
                font_size=5,
                node_color=colour_list,
                linewidths=.5,
                edge_color="DarkGray",
                width=.1)
        elif layout == "spectral":
            nx.draw_spectral(copy_net,
                node_size=size,
                font_size=5,
                node_color=colour_list,
                linewidths=.5,
                edge_color="DarkGray",
                width=.1)
        elif layout == "random":
            nx.draw_random(copy_net,
                node_size=size,
                font_size=5,
                node_color=colour_list,
                linewidths=.5,
                edge_color="DarkGray",
                width=.1)
        # Save figure if applicable
        if fname is not None:
            plt.savefig(fname, bbox_inches="tight")
            print("Wrote file: {} to {}".format(fname, os.getcwd()))

    def describe(self, extra=False):
        """
        Provides a summary of graph statistics. Includes basic statistics like the number of nodes, edges,
        denstiy, and the average degree for one mode. Prints a string that contains each of the items that make up the summary.
        Density is calculated using one of the modes of the original bipartite network graph.

        **Parameters** :

        > *extra* : `bool`

        >> Runs the low efficiency algorithms, which can be resource-intensive on large networks.
        >> Recommended maximum network size for the low efficiency algorithms is around 100 nodes.

        **Returns** : `string`

        > Returns the descriptive string that contains information about the `MultiGraphPlus` object.

        """
        mode1 = self.mode1
        mode2 = self.mode2
        density = bipartite.density(self, bipartite.sets(self)[0])
        edges = self.number_of_edges()
        nodes_mode1 = 0
        nodes_mode2 = 0
        for n in self.nodes():
            if self.node[n]['type'] == mode1:
                nodes_mode1 += 1
            elif self.node[n]['type'] == mode2:
                nodes_mode2 += 1

        descriptives_nodes = "This is a bipartite network of types '{}' and '{}'.\n " \
                             "{} nodes are of the type '{}'.\n " \
                             "{} nodes are of the type '{}'.\n".format(str(mode1), str(mode2), str(nodes_mode1),
                                                                       str(mode1), str(nodes_mode2), str(mode2))
        descriptives_edges = "There are {} edges.\n".format(str(edges))
        descriptives_density = "Density: {}.\n".format(str(density))
        descriptives = descriptives_nodes + descriptives_edges + descriptives_density

        if extra:
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
            g = nx.Graph(self)
            projection = bipartite.projected_graph(g, bipartite.sets(g)[0])
            transitivity = nx.transitivity(projection)
            descriptives_transitivity = "Transitivity: {}.\n".format(str(transitivity))
            descriptives_degree_centrality = "Mean Degree Centrality for '{}': {}.\n" \
                                             "Mean Degree Centrality for '{}': {}.\n".format(str(mode1),
                                                                                             str(degree_mode1),
                                                                                             str(mode2),
                                                                                             str(degree_mode2))
            descriptives_btwn_centrality = "Mean Betweenness Centrality for '{}': {}.\n"\
                                           "Mean Betweenness Centrality for '{}': {}.\n".format(str(mode1),
                                                                                                str(betweenness_mode1),
                                                                                                str(mode2),
                                                                                                str(betweenness_mode2))
            descriptives = descriptives + descriptives_transitivity +\
                descriptives_degree_centrality + descriptives_btwn_centrality
        print(descriptives)
        return descriptives

    def node_merge(self, node1, node2, show_warning=True):
        """
        Combines node1 and node2. After merge, node1 will remain, while node2 will be removed. node2's edges will become
        node1 edges, while retaining all their edge attributes. Vector attributes of node1 and node2 whose
        identifiers match will be combined, retaining all values. Atomic attributes which exist in only one of the
        two nodes will be included in the merge node. Finally, if node1 and node2 contain a conflicting atomic
        attribute, node1's value will overwrite node2's value.

        **Parameters** :

        > *node1* : `string`

        >> The identifier for a node. This node's attributes will persist to the merged node.

        > *node2* : `string`

        >> The identifier for a second node. Any non-conflicting attributes will persist to the merged node.

        > *show_warning* : `bool`

        >> A boolean parameter indicating whether overwrite warnings should be displayed.

        **Return** : `MultiGraphPlus`

        > a new multigraphplus object which has merged nodes 1 and 2 together into node1, which will also have gained node2's edges.

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

        merged_graph.remove_node(node2)  # Removes node2

        if node_merge_warn and show_warning:
            print("Note: nodes '{}' and '{}' have the following conflicting atomic attributes: {}. In these cases, "
                  "'{}' attribute values have been retained, while '{}' values have been ignored. If you would rather "
                  "retain '{}' attributes, set '{}' to node1 and '{}' to node2."
                  .format(node1, node2, node_merge_warn_list, node1, node2, node2, node2, node1))

        return merged_graph

    def collapse_edges(self, sum_weights=False):
        """
        Collapses all edges which share nodes into one edge, with a new weight assigned to it. How this weight is
        assigned depends on the `sum_weights` parameter.

        **Parameters** :

        > *sum_weights* : `bool`

        >> An optional boolean parameter. Determines how weights will be assigned to the final edges.
        >> If False, the weight will be the number of edges which were collapsed. If True, the weight will be the sum of
        >> the weights of collapsed edges.

        **Return** :

        > A new MultiGraphPlus object, which has collapsed all duplicate edges, assigned a new weight, and
        > stores other edge data in lists.

        **Note** :

        > The default weight of an edge is 1. Thus, if sum_weights is set to True, but an edge does not have a
        > weight attribute, this method assumes the weight of the edge is 1.

        """
        gnew = MultiGraphPlus()
        for n1, n2, data in self.edges(data=True):
            if gnew.has_edge(n1, n2):
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
