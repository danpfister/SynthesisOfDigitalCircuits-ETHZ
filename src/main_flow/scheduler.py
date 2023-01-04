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
		self.cdfg.remove_nodes_from([ n for n in get_cdfg_nodes(self.cdfg) if n.attr['type'] == 'br' ]) # remove all branch nodes, they force the II to be the same as iteration latency
		self.cdfg.remove_nodes_from([ n for n in get_cdfg_nodes(self.cdfg) if n.attr['type'] == 'constant' ]) # remove all constant nodes
		backedges = [ (e, dict(e.attr)) for e in get_cdfg_edges(self.cdfg) if e.attr['style'] == 'dashed' ]
		self.cdfg.remove_edges_from([ e[0] for e in backedges])

		leaf_nodes = [] # leaf nodes: all the dfg nodes that have no successors in the same BB
		for n in get_cdfg_nodes(self.cdfg):
			out_edges = list(map(lambda e : (self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1]), self.cdfg.get_edge(*e)), self.cdfg.out_edges(n)))
			if out_edges == [] or any([ n.attr['id'] != v.attr['id'] for n, v, e in out_edges ]):
				leaf_nodes.append(n) # connect the supersink of a BB to all the leaf nodes in the same BB

		root_nodes = [] # root nodes: all the dfg nodes that have no predecessors in the same BB
		for n in get_cdfg_nodes(self.cdfg):
			in_edges = list(map(lambda e : (self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1]), self.cdfg.get_edge(*e)), self.cdfg.in_edges(n)))
			if in_edges == [] or any([ p.attr['id'] != s.attr['id'] for p, s, e in in_edges ]):
				root_nodes.append(n) # connect the supersource of a BB to all the root nodes in the same BB

		for bb in get_cdfg_nodes(self.cfg): # create dummy sources and dummy sinks for each BB
			id_ = bb.attr['id']
			self.cdfg.add_node(f'ssrc_{id_}', id=id_, type = 'supersource', style = 'dashed', label = f'ssrc BB{id_}')
			for n in root_nodes: # connect the super source node to the entering nodes of each BB, that is not a constant (which we have already removed)
				if n.attr['id'] == id_:
					self.cdfg.add_edge(f'ssrc_{id_}', n)
			self.cdfg.add_node(f'ssink_{id_}', id=id_, type = 'supersink', style = 'dashed', label = f'ssink BB{id_}')
			for n in leaf_nodes: # connect the super sink node to the exiting nodes of each BB 
				if n.attr['id'] == id_:
					self.cdfg.add_edge(n, f'ssink_{id_}')
			if self.cdfg.out_edges(f'ssrc_{id_}') == []: # if a bb is empty, add an edge from the supersource to the supersink
				self.cdfg.add_edge(f'ssrc_{id_}', f'ssink_{id_}')

		# ===================== Dependency Constraints ====================== #
		'''
		if there is a forward dependency between node n and v

		n -----> v

		then we say the finishing time of sv_n must be eariler than the starting time of sv_v
		sv_n + latency_n <= sv_v

		'''
		for n, v in map(lambda e : (self.cfg.get_node(e[0]), self.cfg.get_node(e[1])), get_cdfg_edges(self.cfg)):
			if int(n.attr['id']) < int(v.attr['id']): # TODO: handle the backedges as well
				self.cdfg.add_edge(f'ssink_{n.attr["id"]}', f'ssrc_{v.attr["id"]}') # add sequential dependency between BBs

		for n in get_cdfg_nodes(self.cdfg): # create a scheduling variable (sv) per each CDFG node
			ilp.add_variable(f'sv{n}', lower_bound = 0,  var_type="i")

		for e in get_cdfg_edges(self.cdfg): # Dependency constraint: per each edge
			if e.attr['style'] != 'dashed':
				n, v = self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1])
				# sv_v >= sv_n + latency; assume that the latency of each operation is 1 for now
				constraints.add_constraint({f'sv{n}' : -1, f'sv{v}' : 1}, "geq", (1 if n.attr['type'] not in ('supersource', 'supersink') else 0)) 
		# ===================== Dependency Constraints ====================== #

		for e in backedges: # for II constraints, we need to add the backedges back into the graph
			self.cdfg.add_edge(*e[0], **e[1])

		# ===================== II Constraints ====================== #
		'''
		if there is a inter-iteration dependency between node n and v

		n -----> v

		then we say the finishing time of sv_n must be eariler than the starting time of sv_v
		sv_n + latency_n <= sv_v + II * dist_nv

		'''
		for bb in get_cdfg_nodes(self.cfg): # define one II per each BB
			ilp.add_variable(f'II_{bb}', lower_bound = 1, var_type='i')

		for e in get_cdfg_edges(self.cdfg): # cross-iteration constraint: per each backedge
			if e.attr['style'] == 'dashed':
				n, v = self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1])
				assert n.attr['bbID'] == v.attr['bbID'], 'sanity check failed: II defined only for single BB for now'
				# sv_n + latency_u <= sv_v + II * Dist; if there is an back edge assume that for now the dependencies from the back edges all have dist = 1
				# TODO: determine the dependency distance?
				constraints.add_constraint({ f'sv{n}' : -1, f'sv{v}' : 1, f'II_{n.attr["bbID"]}' : 1 }, "geq", (1 if n.attr['type'] not in ('supersource', 'supersink') else 0)) 
		# ===================== II Constraints ====================== #

		fun = Opt_Function(ilp)

		## ======================== Latency Minimization Objective ==========================#
		## objective: minimize the end-to-end latency
		#ilp.add_variable(f'max_latency', lower_bound = 0,  var_type="i")
		#fun.add_variable(f'max_latency', 1)

		#ssinks = filter(lambda n : n.attr['type'] == 'supersink', get_cdfg_nodes(self.cdfg))
		#for n in ssinks: # we try to minimize the latest SSINK
		#	constraints.add_constraint({f'sv{n}' : -1, f'max_latency' : 1}, "geq", 0)
		## ======================== Latency Minimization Objective ==========================#

		# ======================== II Minimization Objective ===============================#
		ilp.add_variable(f'max_II', lower_bound = 0,  var_type="i")
		fun.add_variable(f'max_II', 1)
		for bb in get_cdfg_nodes(self.cfg): # TODO: only minimize the II of the loop BB
			constraints.add_constraint({f'II_{bb}' : -1, 'max_II' : 1}, 'geq', 0)
		# ======================== II Minimization Objective ===============================#

		# log the result
		self.cdfg.draw("test_dag.pdf", prog="dot")
		ilp.print_ilp("{0}/{1}/output.lp".format(base_path, example_name))
		res = ilp.solve_ilp()
		print(res)
		pprint(ilp.get_ilp_solution())
		if 'max_latency' in ilp.get_ilp_solution():
			print(f'the maximum latency for this cdfg is {ilp.get_ilp_solution()["max_latency"]}')
		elif 'max_II' in ilp.get_ilp_solution():
			print(f'the maximum II for this cdfg is {ilp.get_ilp_solution()["max_II"]}')

