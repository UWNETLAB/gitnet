library(igraph)

# Set the working directory to your own preferred directory.
# Something like 'C:/users/user/Desktop/' would work well in Windows.
# Something like '~/Users/user/Desktop/' should work on OSX or Linux.

setwd("C:/users/user/Desktop/")

# Import the GRAPHML file exported from gitnet.
# See the gitnet walkthrough if you do not know how to create and export a GRAPHML file.

G <- read.graph("mygraph.graphml", format = c("graphml"))

# The removes multiple edges from the plot.
# Since graphs created with gitnet are multigraphs (with multiple edges),
# it is best to only use this when you want to make a simple looking plot, not for analysis.

G <- simplify(G, remove.multiple = TRUE, remove.loops = TRUE,
         edge.attr.comb = igraph_opt("edge.attr.comb"))

# These are some settings that look pretty good.

V(G)$size = 3 # Set vertex size, slightly smaller than the default.
E(G)$width = 1 # Set edge size.
V(G)$label.cex = 0.4 # Change the size of labels.
V(G)$label.color = "black"

# There is some customization here. Depending on the modes you used in your graph, you can specify colours.
# If you chose to add colours (simple or complex), you could select new mappings for them here:
# V(G)[colour == "original"]$color = "new"

V(G)[type == "author"]$color = "oldlace"
V(G)[type == "files"]$color = "lightcoral"

lay = layout.kamada.kawai(G)

# This saves the plot as a pdf in the current directory.

pdf("myplot.pdf")
par(mar=c(0,0,0,0)+.5)
plot(G, layout = lay, vertex.label = NA)
dev.off()
