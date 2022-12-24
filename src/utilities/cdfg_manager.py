
# function to retrieve edges of cdfg
def get_cdfg_edges(cdfg):
	return map(lambda e : cdfg.get_edge(*e), cdfg.edges(keys=True))

# function to retrieve nodes of cdfg
def get_cdfg_nodes(cdfg):
	return map(lambda n : cdfg.get_node(n), cdfg.nodes())
