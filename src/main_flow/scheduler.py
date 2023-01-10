from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
from pprint import pprint
import re
import logging

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
#					- log: logger object used to output logs
############################################################################################################################################
#	FUNCTIONS:
#					- set_sched_technique : set scheduling technique
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
	def __init__(self, parser, sched_technique, log=None):
		if log != None:
			self.log = log
		else:
			self.log = logging.getLogger('scheduler') # if the logger is not given at object generation, create a new one
		self.parser = parser
		self.cdfg = parser.get_cdfg()
		self.cfg = parser.get_cfg()
		self.set_sched_technique(sched_technique)

		# set solver options
		self.ilp = ILP(log=log)
		self.constraints = Constraint_Set(self.ilp, log=log)
		self.opt_fun = Opt_Function(self.ilp, log=log)

		# remove all branch nodes, they force the II to be the same as iteration latency
		self.cdfg.remove_nodes_from([ n for n in get_cdfg_nodes(self.cdfg) if n.attr['type'] == 'br' ]) 

		# remove all constant nodes
		self.cdfg.remove_nodes_from([ n for n in get_cdfg_nodes(self.cdfg) if n.attr['type'] == 'constant' ]) 

		# add one ilp variable per each node
		for n in get_cdfg_nodes(self.cdfg): # create a scheduling variable (sv) per each CDFG node
			self.ilp.add_variable(f'sv{n}', lower_bound = 0,  var_type="i")
	

	# function to set scheduling technique
	def set_sched_technique(self, technique):
		assert(technique in scheduling_techniques) # the scheduling technique chosen must belong to the allowed ones
		self.log.info(f'setting the scheduling technique to be "{technique}"')
		self.sched_tech = technique

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
				self.log.debug(f'adding dependency constraint {n} -> {v}')
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
		self.log.debug(f'topological ordering: {topological_order}')
		# assume the following resource constraints:
		# load port <= 2; adders <= 1;
		resource_constraint = { 'load' : 2, 'add' : 1 }

		# resource constraints are done within each BB
		for bb in get_cdfg_nodes(self.cfg):
			for res, max_ in resource_constraint.items():
				self.log.debug(f'adding resource constaint: {res} has maximum of {max_} inside BB {bb}')
				# get all the nodes that have resource type res inside the bb
				res_topological_order = [ n for n in topological_order
					if self.cdfg.get_node(n).attr['type'] == res and self.cdfg.get_node(n).attr['bbID'] == bb ]
				self.log.debug(f'nodes of type {res} in BB {bb}: {res_topological_order}')
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
					self.log.debug(f'resource constraint between {n} and {v}')
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
		for e in get_back_edges(self.cdfg): 
			self.log.debug(f'adding II constraint for backedge: {e[0]} -> {e[1]}')
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
			self.log.error(f'Not implemented option! {self.sched_tech}')
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
			self.log.info(f'{var} of type {type_}:= {value}')
		self.cdfg.draw("test_dag_result.pdf", prog="dot")
		if 'max_latency' in self.ilp.get_ilp_solution():
			self.log.info(f'the maximum latency for this cdfg is {self.ilp.get_ilp_solution()["max_latency"]}')
		elif 'max_II' in self.ilp.get_ilp_solution():
			self.log.info(f'the maximum II for this cdfg is {self.ilp.get_ilp_solution()["max_II"]}')

