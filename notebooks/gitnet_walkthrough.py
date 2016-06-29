
# coding: utf-8

# # User Testing gitnet
#
# #### *June 2016, using version 0.0.8 of gitnet on testpypi*
#

#
# ## *Introduction*
#

# To follow this exercise successfully, you need to have:
# - Python 3 (Anacondas 3.5 is the best bet)
# - Git (you can update git by running in the terminal: pip install git --upgrade)
#     - The current version of gitnet is 0.0.8.
# - NetworkX (you can install by running in ther terminal: pip install networkx)
# - Matplotlib (you can install by running in the terminal: pip install matplotlib)
# - Pygraphviz (not neccessarily required, only for the default layout, which happens to be the best one we could find)
#
# **Note:** Unfortunately, Pygraphviz can potentially be difficult to install on Windows. If pip is not able to find vcvarsall.bat, then avoid editing the environment variables and use this website: http://www.lfd.uci.edu/~gohlke/pythonlibs/ to download the binary for Python 3.4. Unfortunately, although Pygraphviz will install, there still may be errors with the graph output.
#
# Installing gitnet with pip will automatically install bash if you do not already have it installed
# To install gitnet, open a terminal window and type:
#
# `pip install -i https://testpypi.python.org/pypi gitnet`

# For all sections of this exercise, you will need to use the following libraries:

import os
# import pygraph # Needed for defaults used by quickplot, if you can't install, use layout='spring'.
import gitnet as gn
import networkx as nx
import matplotlib.pyplot as plt


# ## *1. Write-Good Repo*

# For this exercise, we are going to use the project: https://github.com/btford/write-good
#
# In a new terminal window, type:
#
# `git clone https://github.com/btford/write-good.git`
#
# OR open the page in a browser and download the zip folder.

# Set the current working directory, so that all files created will be stored there.
# The best bet is to create a folder named 'temp' on your desktop.
os.chdir('path')

# Insert the path to the write-good folder on your machine.
mylogs = gn.get_log('path')
# You can generate a network using any two tags that exist in the log. For a list of tags, just call .attributes() on your log object.
graph = mylogs.generate_network('author', 'files')
# Quickplot is a preset function that can be used to quickly visualize a network.
graph.quickplot('write_good_net.pdf', layout = 'spring')

# You can get a list of all of the values of any tag in the log object.
# First, lets take a look at all of the possible tags.
print(mylogs.attributes())
# Now, lets print that list of values. Choose one of the tags from above.
print(mylogs.vector('date'))


# ## *2. NetworkX*

# For this exercise, we are going to use this project: https://github.com/networkx/networkx
#
# In a new terminal window, type:
#
# `git clone https://github.com/networkx/networkx.git`
#
# OR open the page in a browser and download the zip folder.

# First, we are going to create another log object.
networkx_log = gn.get_log('path')

# Now you can export the log as a TSV file.
networkx_log.tsv(fname = 'networkx_data.tsv')


# Take a minute to open this file and look at the contents.
#
# Notice that there are similar author names that use the same email address.
#
# **Hint:** since version 0.0.8, we have simplified the process of identifying duplicate authors.
# Use `author_email_list` along with `detect_dup_emails` to find potentially duplicate authors. See the cheat sheet for more details.

# Gitnet cannot automatically predict when a single author uses two different names to commit to a repo.
# For this reason, you may need to use replace one of their aliases with the other.
replaced_netx = networkx_log.replace_val('author', 'aric', 'Aric Hagburg')
# To make sure that this worked, just create a new TSV and look at the contents.
replaced_netx.tsv(fname = 'replaced_data.tsv')

# You can also create an edgelist from any two tags.
# Check the possible tags.
print(replaced_netx.attributes())
# Then use whichever ones you want to generate an edgelist.
replaced_netx.write_edges('edgelist.txt', 'author', 'files')


# *Optional:* you can now read this file into R as an edgelist

# ## *3. Tensorflow*

# For this exercise, we are going to use this project: https://github.com/tensorflow/tensorflow
#
# In a new terminal window, type:
#
# `git clone https://github.com/tensorflow/tensorflow.git`
#
# OR open the page in a browser and download the zip folder.

# Lets start by creating a log object and a graph object, just as in the first exercise.
logs_tensor = gn.get_log('path')
graph_tensor = logs_tensor.generate_network('author', 'files')

# For now, hold off on plotting or exporting, and try out some of the advanced methods
#
# Below are some usage examples for filter and ignore

# Filter seems to have an error in IPYNB format.

# Filter records based on the email domain.
filtered_email = logs_tensor.filter('email', 'has', '@gmail.com')
# Filter records based on the author name.
filtered_author = logs_tensor.filter('author', 'equals', 'Martin Wicke')
# Filter records based on commits that have occured after a certain date.
filtered_date = logs_tensor.filter('date', 'since', 'Fri Jun 10 15:41:25 2016 -0400')

# One of the limitations of filter is that because of the date-string format used by git, you need to type a pattern that at least partially matches the appearance of date-strings in the actually commits.
#
# However, it is still possible to use expressions such as `Fri June 10 *`, so there is still some room for flexible filtering.

# Save one of these to a TSV file to check that it worked.
filtered_author.tsv(fname = 'tensorflow_martin.tsv')

# You can also ignore files and file edits that match any specified patter.
# Ignore python files:
ignore_python = logs_tensor.ignore('.py')
# Ignore files with the _ prefix:
ignore_prefix = logs_tensor.ignore('_*')


# Keep in mind that both `filter` and `ignore` can have a significant impact on the network graph.
#
# It is best to use them sparingly, and only when it is certainly useful to remove certain information.
# In many cases, it makes more sense to simply export the full graph and all its data (as a graphml file, for example) and then prune the data in R.

# Save one of these to a TSV file to check that it worked.
ignore_python.tsv(fname = 'nopy_data.tsv')

# Try generating a network using one of these modified log objects, and compare it to previous results.
modified_graph = ignore_python.generate_network('author', 'files')
modified_graph.quickplot('modified_graph.pdf', layout = 'spring') # this runs very slow.


# One note about the quickploy function is that it typically uses the `neato` layout from `matplotlib`.
#
# Here we are using the `spring` layout from `NetworkX`, but if you did get matplotlib installed, then you can simply leave
# out the layout argument. It defaults to `neato`.

# Try calling describe on both a log object and a graph object.
# Is there any other information you would like to see in the describe output?
ignore_python.describe()
modified_graph.describe()


# The last advanced method we have to show you is collapse graph. This quickly creates a one-mode network, using *mode1* of the
# original graph object.

# Try calling one of the advanced graph methods, such as *collapse_edges*
basic_graph = logs_tensor.generate_network('author', 'files')
# Sum_weights = True is an optional argument that creates a weighted multigraph.
collapsed_graph = basic_graph.collapse_edges(sum_weights = True)
collapsed_graph.quickplot(fname = "ok_net.pdf")


# Optional: try reading an output file into R.
#
# Use the edge list created earlier, or create a new *tnet file* or *graphml file* and try reading it into R.

# The graphml file will be saved at the directed path, while the tnet file will be saved in the current directory.
basic_graph.write_tnet('filename')
basic_graph.write_graphml('path/to/file')


# If you prefer, you can use two columns of the TSV file as the 'source' and 'target' of a networkx graph object in R.
