
# function to retrieve edges of cdfg
def get_cdfg_edges(cdfg):
	return map(lambda e : cdfg.get_edge(*e), cdfg.edges(keys=True))

# function to retrieve nodes of cdfg
def get_cdfg_nodes(cdfg):
	return map(lambda n : cdfg.get_node(n), cdfg.nodes())

# function to update the value of a key (where the value is a list)
def update_dic_list(dic, key, new_element):
	if key in dic:
		inst_list = dic[key]
	else:
		inst_list = []
	inst_list.append(new_element)
	dic[key] = inst_list
	return dic