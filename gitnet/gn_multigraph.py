import networkx as nx
import warnings
import matplotlib.pyplot as plt
import copy
from networkx.drawing.nx_agraph import graphviz_layout


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

    def quickplot(self, layout = "spring", fname = None, size = 20):
        """
        Makes a quick visualization of the network.
        :param layout: The type of layout to draw. ("spring", "circular", "shell", "spectral", or "random")
        :param fname: If specified, a copy of the figure is saved using this file name.
        :param size: The size of the nodes. Default is 20.
        :return: None
        """
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
                colour_data[n] = "lightgrey"
        colour_list = [colour_data[node] for node in copy_net.nodes()]
        # Plot the network
        if layout in ["dot", "neato", "fdp", "sfdp", "twopi", "circo"]:
            nx.draw(copy_net,
                    pos = graphviz_layout(copy_net,prog=layout),
                    node_size = size,
                    font_size = 5,
                    node_color = colour_list,
                    linewidths = .5,
                    edge_color = "DarkGray",
                    width = .1)
                    #k = .01,
                    #iterations = 100)
        if layout == "spring":
            nx.draw_spring(copy_net,
                            node_size = size,
                            font_size = 5,
                            node_color =colour_list,
                            linewidths = .5,
                            edge_color = "DarkGray",
                            width = .1,
                            k = .01,
                            iterations=100)
        elif layout == "circular":
            nx.draw_circular(copy_net,
                            node_size = size,
                            font_size = 5,
                            node_color =colour_list,
                            linewidths = .5,
                            edge_color = "DarkGray",
                            width = .1,
                            k = 1000)
        elif layout == "shell":
            nx.draw_shell(copy_net,
                           node_size=size,
                           font_size=5,
                           node_color =colour_list,
                           linewidths=.5,
                           edge_color="DarkGray",
                           width=.1,
                           k=1000)
        elif layout == "spectral":
            nx.draw_spectral(copy_net,
                           node_size=size,
                           font_size=5,
                           node_color =colour_list,
                           linewidths=.5,
                           edge_color="DarkGray",
                           width=.1,
                           k=1000)
        elif layout == "random":
            nx.draw_random(copy_net,
                           node_size=size,
                           font_size=5,
                           node_color =colour_list,
                           linewidths=.5,
                           edge_color="DarkGray",
                           width=.1,
                           k=1000)
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
