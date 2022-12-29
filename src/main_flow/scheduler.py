from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
from pprint import pprint

############################################################################################################################################
############################################################################################################################################
#
#	`SCHEDULER` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#					The following class is used as a scheduler a CDFG (Control DataFlow Graph) representing a function. 
# 					It elaborates the CDFG of an IR (Intermediare Representation).
#					Then, it generates its scheduling depending on the scheduling technique selected
############################################################################################################################################
#	ATTRIBUTES:
#					- parser : parser used to generate CDFG after parsing SSA IR
#					- cdfg : CDFG representation of the SSA IR input
#					- cfg : CFG representation of the SSA IR input
#					- sched_tech : scheduling technique selected
############################################################################################################################################
#	FUNCTIONS:
#					- set_sched_technique : set scheduling technique
############################################################################################################################################
############################################################################################################################################

scheduling_techniques = ["no_pipeline"]

class Scheduler:

	# initialization of the scheduler with the parser
	def __init__(self, parser, sched_technique):
		self.parser = parser
		self.cdfg = parser.get_cdfg()
		self.cfg = parser.get_cfg()
		self.set_sched_technique(sched_technique)

	# function to set scheduling technique
	def set_sched_technique(self, technique):
		assert(technique in scheduling_techniques) # the scheduling technique chosen must belong to the allowed ones
		self.sched_tech = technique

	# function to test correct functionality of ILP
	def ilp_test(self, base_path, example_name):
		ilp = ILP()
		ilp.add_variable("var1", var_type="b")
		ilp.add_variable("var2", var_type="b")
		constraints = Constraint_Set(ilp)
		constraints.add_constraint({"var1":2, "var2":1}, "geq", 2)
		fun = Opt_Function(ilp)
		fun.add_variable("var1", 1)
		fun.add_variable("var2", 1)
		ilp.print_ilp("{0}/{1}/output.lp".format(base_path, example_name))
		res = ilp.solve_ilp()
		print(res)
		print(ilp.get_ilp_solution())

	# test running ILP on CDFG without all backedges removed
	def ilp_test2(self, base_path, example_name):
		ilp = ILP()
		constraints = Constraint_Set(ilp)

		# daggify: remove all the back edges and constants
		self.cdfg.remove_edges_from([ e for e in get_cdfg_edges(self.cdfg) if e.attr['style'] == 'dashed' ])
		self.cdfg.remove_nodes_from([ n for n in get_cdfg_nodes(self.cdfg) if n.attr['type'] == 'constant' ])

		leaf_nodes = [] # leaf nodes: all the dfg nodes that have no successors in the same BB
		for n in get_cdfg_nodes(self.cdfg):
			out_edges = list(map(lambda e : (self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1]), self.cdfg.get_edge(*e)), self.cdfg.out_edges(n)))
			if out_edges == [] or any([ n.attr['id'] != v.attr['id'] for n, v, e in out_edges ]):
				leaf_nodes.append(n)

		root_nodes = [] # root nodes: all the dfg nodes that have no predecessors in the same BB
		for n in get_cdfg_nodes(self.cdfg):
			in_edges = list(map(lambda e : (self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1]), self.cdfg.get_edge(*e)), self.cdfg.in_edges(n)))
			if in_edges == [] or any([ n.attr['id'] != v.attr['id'] for n, v, e in in_edges ]):
				root_nodes.append(n)

		for bb in get_cdfg_nodes(self.cfg): # create dummy sources and dummy sinks for bbs
			id_ = bb.attr['id']
			self.cdfg.add_node(f'ssrc_{id_}', id=id_, type = 'supersource', style = 'dashed', label = f'ssrc BB{id_}')
			for n in root_nodes:
				if n.attr['id'] == id_:
					self.cdfg.add_edge(f'ssrc_{id_}', n)
			self.cdfg.add_node(f'ssink_{id_}', id=id_, type = 'supersink', style = 'dashed', label = f'ssink BB{id_}')
			for n in leaf_nodes:
				if n.attr['id'] == id_:
					self.cdfg.add_edge(n, f'ssink_{id_}')
			if self.cdfg.out_edges(f'ssrc_{id_}') == []: # if a bb is empty, add an edge from the supersource to the supersink
				self.cdfg.add_edge(f'ssrc_{id_}', f'ssink_{id_}')

		for n, v in map(lambda e : (self.cfg.get_node(e[0]), self.cfg.get_node(e[1])), get_cdfg_edges(self.cfg)):
			if int(n.attr['id']) < int(v.attr['id']): # TODO: handle the backedges as well
				self.cdfg.add_edge(f'ssink_{n.attr["id"]}', f'ssrc_{v.attr["id"]}') # add sequential dependency between BBs

		for n in get_cdfg_nodes(self.cdfg): # create a scheduling variable (sv) per each CDFG node
			ilp.add_variable(f'sv{n}', lower_bound = 0,  var_type="i")

		for e in get_cdfg_edges(self.cdfg): # Dependency constraint: per each edge
			n, v = self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1])
			constraints.add_constraint({f'sv{n}' : -1, f'sv{v}' : 1}, "geq", (1 if n.attr['type'] not in ('supersource', 'supersink') else 0)) # sv_v >= sv_n + latency; assume that the latency of each operation is 1 for now
		fun = Opt_Function(ilp)

		# objective: minimize the end-to-end latency
		ilp.add_variable(f'max_latency', lower_bound = 0,  var_type="i")
		fun.add_variable(f'max_latency', 1)

		ssinks = filter(lambda n : n.attr['type'] == 'supersink', get_cdfg_nodes(self.cdfg))
		for n in ssinks: # we try to minimize the latest SSINK
			constraints.add_constraint({f'sv{n}' : -1, f'max_latency' : 1}, "geq", 0)

		# log the result
		self.cdfg.draw("test_dag.pdf", prog="dot")
		ilp.print_ilp("{0}/{1}/output.lp".format(base_path, example_name))
		res = ilp.solve_ilp()
		print(res)
		pprint(ilp.get_ilp_solution())
		print(f'the maximum latency for this cdfg is {ilp.get_ilp_solution()["max_latency"]}')


