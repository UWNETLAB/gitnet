import gitnet as gn

nx_log0 = gn.get_log("/Users/joelbecker/Documents/Work/Networks Lab/Test Repo/networkx")

nx_log1 = nx_log0.filter("files","has","networkx/algorithms/flow/mincost.py").filter("author","has","Loïc")

nx_log1.browse()
