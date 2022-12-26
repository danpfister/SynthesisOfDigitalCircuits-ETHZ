############################################################################################################################################
############################################################################################################################################
#
#	CDFG MANAGER
#
############################################################################################################################################
#	FUNCTIONS:
#				- get_cdfg_edges : retrieve edges of cdfg
#				- get_cdfg_nodes : retrieve nodes of cdfg
#				- update_dic_list : update the value of a key (where the value is a list)
#				- create_control_edge : create a control edge between src and dst in the cdfg
#				- is_control_edge : check if edge between src and dst is a control edge
############################################################################################################################################
############################################################################################################################################


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

# function to create a control edge between src and dst in the cdfg
def create_control_edge(cdfg, src, dst):
	cdfg.add_edge(src, dst, style="dashed")
	return cdfg

# function to check if edge between src and dst is a control edge
def is_control_edge(cdfg, src, dst):
	pass