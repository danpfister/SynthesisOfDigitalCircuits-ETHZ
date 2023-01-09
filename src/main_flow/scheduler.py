from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
from pprint import pprint
import re
import logging

log = logging.getLogger('sdc.scheduler') # logger

############################################################################################################################################
############################################################################################################################################
#
#	`SCHEDULER` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#					The following class is used as a scheduler a CDFG (Control DataFlow Graph) representing a function. 
#					It elaborates the CDFG of an IR (Intermediare Representation).
#					Then, it generates its scheduling depending on the scheduling technique selected
############################################################################################################################################
#	ATTRIBUTES:
#					- parser : parser used to generate CDFG after parsing SSA IR
#					- cdfg : CDFG representation of the SSA IR input
#					- cfg : CFG representation of the SSA IR input
#					- sched_tech : scheduling technique selected
#					- ilp: ilp object
#					- constraints: constraints object
#					- opt_fun: optmization function object
############################################################################################################################################
#	FUNCTIONS:
#					- set_sched_technique : set scheduling technique
#					- add_artificial_nodes : add artificial nodes (supersource and supersink) to form a hierarchical sequencing graph
#					- set_data_dependency_constraints: add data dependency constraints to the constraints
#					- set_resource_constraints: add resource dependency constraints to the constraints
#					- set_II_constraints: add II constraints to the constraints
#					- set_opt_function: set optimization function according to the self.sched_tech
#					- find_optimal_schedule: run the solver on top of the constrants from set_*_constraints and the objective function from set_opt_function
############################################################################################################################################
############################################################################################################################################


scheduling_techniques = ["no_pipeline", "pipelined"]

class Scheduler:

	# initialization of the scheduler with the parser
	def __init__(self, parser, sched_technique):
		self.parser = parser
		self.cdfg = parser.get_cdfg()
		self.cfg = parser.get_cfg()
		self.set_sched_technique(sched_technique)

		# set solver options
		self.ilp = ILP()
		self.constraints = Constraint_Set(self.ilp)
		self.opt_fun = Opt_Function(self.ilp)

		# remove all branch nodes, they force the II to be the same as iteration latency
		self.cdfg.remove_nodes_from([ n for n in get_cdfg_nodes(self.cdfg) if n.attr['type'] == 'br' ]) 

		# remove all constant nodes
		self.cdfg.remove_nodes_from([ n for n in get_cdfg_nodes(self.cdfg) if n.attr['type'] == 'constant' ]) 

		# adding supersource and supersinks to the cdfg
		self.add_artificial_nodes()

		# add one ilp variable per each node
		for n in get_cdfg_nodes(self.cdfg): # create a scheduling variable (sv) per each CDFG node
			self.ilp.add_variable(f'sv{n}', lower_bound = 0,  var_type="i")
	

	# function to set scheduling technique
	def set_sched_technique(self, technique):
		assert(technique in scheduling_techniques) # the scheduling technique chosen must belong to the allowed ones
		log.info(f'setting the scheduling technique to be "{technique}"')
		self.sched_tech = technique

	# add supersource and supersink nodes to each BB
	# TODO: maybe we move this function to the parser
	def add_artificial_nodes(self):
		# leaf nodes: all the exiting nodes of BBs
		leaf_nodes = [] 
		for n in get_cdfg_nodes(self.cdfg):
			# get all edges that are not back edges
			out_edges = [ e for e in get_dag_edges(self.cdfg) if str(e[0]) == str(n)]

			# if n has no predecessors, then for sure we connect it to supersource
			if out_edges == []:
				leaf_nodes.append(n)
			# if n has predecessors from a different BB, then we connect it to a supersource
			else:
				for e in out_edges:
					id_pred = self.cdfg.get_node(e[0]).attr['id']
					id_succ = self.cdfg.get_node(e[1]).attr['id']
					if id_pred != id_succ:
						leaf_nodes.append(n)
						break
		
		# root_nodes: all the entering nodes of BBs
		root_nodes = [] # root nodes: all the dfg nodes that have no predecessors in the same BB
		for n in get_cdfg_nodes(self.cdfg):
			in_edges = [ e for e in get_dag_edges(self.cdfg) if str(e[1]) == str(n)]

			# if n has no successors, then for sure we connect it to a supersink
			if in_edges == []:
				root_nodes.append(n)
			# if n has successors from a different BB, then we connect it to a supersink
			else:
				for e in in_edges:
					id_pred = self.cdfg.get_node(e[0]).attr['id']
					id_succ = self.cdfg.get_node(e[1]).attr['id']
					if id_pred != id_succ:
						leaf_nodes.append(n)
						break

		# connect the root nodes and the leaf nodes to supernodes
		for bb in get_cdfg_nodes(self.cfg):
			id_ = bb.attr['id']
			self.cdfg.add_node(f'ssrc_{id_}',id=id_,type='supersource',style='dashed',label=f'ssrc BB{id_}')
			# connect the super source node to the entering nodes of each BB, that is not a constant (which we have already removed)
			for n in root_nodes: 
				if n.attr['id'] == id_:
					self.cdfg.add_edge(f'ssrc_{id_}', n)
			self.cdfg.add_node(f'ssink_{id_}', id=id_, type = 'supersink', style = 'dashed', label = f'ssink BB{id_}')
			# connect the super sink node to the exiting nodes of each BB 
			for n in leaf_nodes: 
				if n.attr['id'] == id_:
					self.cdfg.add_edge(n, f'ssink_{id_}')
			if self.cdfg.out_edges(f'ssrc_{id_}') == []: # if a bb is empty, add an edge from the supersource to the supersink
				self.cdfg.add_edge(f'ssrc_{id_}', f'ssink_{id_}')

		# establish connections between supersource and supersink according to control-flow graph
		for n, v in map(lambda e : (self.cfg.get_node(e[0]), self.cfg.get_node(e[1])), get_cdfg_edges(self.cfg)):
			if int(n.attr['id']) < int(v.attr['id']): # TODO: handle the backedges as well
				self.cdfg.add_edge(f'ssink_{n.attr["id"]}', f'ssrc_{v.attr["id"]}') # add sequential dependency between BBs
		self.cdfg.draw("test_supernodes.pdf", prog="dot")

	''' function for setting the data dependency constraint between two nodes '''
	def set_data_dependency_constraints(self):
		'''
		if there is a forward dependency between node n and v

		n -----> v

		then we say the finishing time of sv_n must be eariler than the starting time of sv_v
		sv_n + latency_n <= sv_v

		'''
		for e in get_cdfg_edges(self.cdfg): # Dependency constraint: per each edge
			if e.attr['style'] != 'dashed':
				n, v = self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1])
				log.debug(f'adding dependency constraint {n} -> {v}')
				# sv_v >= sv_n + latency; assume that the latency of each operation is 1 for now
				self.constraints.add_constraint({f'sv{n}' : -1, f'sv{v}' : 1}, "geq", get_node_latency(n.attr) )

	''' function for setting up the maximum resource usage per res type '''
	def set_resource_constraints(self):
		""" 
		exact resource-constraint scheduling is NP-hard to compute. we use 
		a heuristic operates on linear ordering of operations:

		suppose for operation mul, we have only 2 available resources for mul:
		(1) identify a linear ordering between operations inside BB of interest:
			mul_0, mul_1, mul_2, mul_3, mul_4
		(2) for every pair of nodes that require mul, we count the number of mul's within them
			Between(mul_0, mul_2) = { mul_1 }
		(3) check if in the set Between(), there are RESOURCE(mul) - 1 nodes:
			RESOURCE(mul) - 1 = 1, which is the same as Between(mul_0, mul_2)
		(4) then, we add an additional constaint to enforce that mul_0 and mul_2 can't be scheduled together
			sv_(mul_0) + lat_(mul_0) <= sv_(mul_2)
		"""
		topological_order = get_topological_order(self.cdfg)
		log.debug(f'topological ordering: {topological_order}')
		# assume the following resource constraints:
		# load port <= 2; adders <= 1;
		resource_constraint = { 'load' : 2, 'add' : 1 }

		# resource constraints are done within each BB
		for bb in get_cdfg_nodes(self.cfg):
			for res, max_ in resource_constraint.items():
				log.debug(f'adding resource constaint: {res} has maximum of {max_} inside BB {bb}')
				# get all the nodes that have resource type res inside the bb
				res_topological_order = [ n for n in topological_order
					if self.cdfg.get_node(n).attr['type'] == res and self.cdfg.get_node(n).attr['bbID'] == bb ]
				log.debug(f'nodes of type {res} in BB {bb}: {res_topological_order}')
				# (2), (3): for each pair of nodes that have (RESOURCE - 1) nodes in between
				for i in range(len(res_topological_order)):
					n = res_topological_order[i]
					try:
						v = res_topological_order[ i + max_ ]
					except IndexError:
						continue
					'''
					n dominates v in topological order, and there are already RESOURCE number of operations before v
					
					'''
					log.debug(f'resource constraint between {n} and {v}')
					# (4): add constraint
					self.constraints.add_constraint({f'sv{n}' : -1, f'sv{v}' : 1}, "geq", get_node_latency(n.attr) )
	
	''' function for setting the initialization interval constraint from the back edges '''
	def set_II_constraints(self):
		assert self.sched_tech != 'no_pipeline', 'sanity check'
		# ===================== II Constraints ====================== #
		'''
		if there is a inter-iteration dependency between node n and v

		n -----> v

		then we say the finishing time of sv_n must be eariler than the starting time of sv_v
		sv_n + latency_n <= sv_v + II * dist_nv

		'''
		# define one II per each BB
		for bb in get_cdfg_nodes(self.cfg): 
			self.ilp.add_variable(f'II_{bb}', lower_bound = 1, var_type='i')

		# cross-iteration constraint: per each backedge
		for e in get_bak_edges(self.cdfg): 
			log.debug(f'adding II constraint for backedge: {e[0]} -> {e[1]}')
			n, v = self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1])
			assert n.attr['bbID'] == v.attr['bbID'], 'sanity check failed: II defined only for single BB for now'
			# sv_n + latency_u <= sv_v + II * Dist; if there is an back edge assume that for now the dependencies from the back edges all have dist = 1
			# TODO: determine the dependency distance?
			self.constraints.add_constraint({ f'sv{n}' : -1, f'sv{v}' : 1, f'II_{n.attr["bbID"]}' : 1 }, "geq", get_node_latency(n.attr)) 

	''' function for setting the optimiztion funciton, according to the optimization option '''
	def set_opt_function(self):
		if self.sched_tech == 'no_pipeline':
			# ======================== Latency Minimization Objective ==========================#
			# objective: minimize the end-to-end latency
			self.ilp.add_variable(f'max_latency', lower_bound = 0,  var_type="i")
			self.opt_fun.add_variable(f'max_latency', 1)

			ssinks = filter(lambda n : n.attr['type'] == 'supersink', get_cdfg_nodes(self.cdfg))
			for n in ssinks: # we try to minimize the latest SSINK
				self.constraints.add_constraint({f'sv{n}' : -1, f'max_latency' : 1}, "geq", 0)
		elif self.sched_tech == 'pipelined':
			# ======================== II Minimization Objective ===============================#
			self.ilp.add_variable(f'max_II', lower_bound = 0,  var_type="i")
			self.opt_fun.add_variable(f'max_II', 1)
			for bb in get_cdfg_nodes(self.cfg): # TODO: only minimize the II of the loop BB
				self.constraints.add_constraint({f'II_{bb}' : -1, 'max_II' : 1}, 'geq', 0)
		else:
			log.error(f'Not implemented option! {self.sched_tech}')
			raise NotImplementedError

	''' find the optimal schedule for the given scheduling problem '''
	def find_optimal_schedule(self, base_path, example_name):
		# log the result
		self.ilp.print_ilp("{0}/{1}/output.lp".format(base_path, example_name))
		res = self.ilp.solve_ilp()
		for var, value in self.ilp.get_ilp_solution().items():
			type_ = 'AUX'
			if re.search(r'^sv', var):
				node_name = re.sub(r'^sv', '', var)
				attr = self.cdfg.get_node(node_name).attr
				type_ = attr['type']
				attr['label'] = attr['label'] + '\n' + f'[{value}]'
			log.info(f'{var} of type {type_}:= {value}')
		self.cdfg.draw("test_dag_result.pdf", prog="dot")
		if 'max_latency' in self.ilp.get_ilp_solution():
			log.info(f'the maximum latency for this cdfg is {self.ilp.get_ilp_solution()["max_latency"]}')
		elif 'max_II' in self.ilp.get_ilp_solution():
			log.info(f'the maximum II for this cdfg is {self.ilp.get_ilp_solution()["max_II"]}')

