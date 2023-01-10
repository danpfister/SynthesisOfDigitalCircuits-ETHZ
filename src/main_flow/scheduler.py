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
#					- sched_sol : scheduling solution
#					- ilp: ilp object
#					- constraints: constraints object
#					- opt_fun: optmization function object
#					- log: logger object used to output logs
############################################################################################################################################
#	FUNCTIONS:
#					- set_sched_technique : set scheduling technique
#					- set_data_dependency_constraints: add data dependency constraints to the constraints
#					- set_II_constraints: add II constraints to the constraints
#					- set_opt_function: set optimization function according to the self.sched_tech
#					- create_scheduling_ilp : create the ILP of the scheduling
#					- solve_scheduling_ilp: run the solver on top of the constrants from set_*_constraints and the objective function from set_opt_function
#					- get_ilp_tuple : get ilp, constraints and optimization function
#					- print_gantt_chart : prints the gantt chart of a scheduling solution
############################################################################################################################################
############################################################################################################################################


scheduling_techniques = ["no_pipeline", "asap", "alap", "pipelined"]

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
		self.sched_sol = None

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
		self.log.info(f'Setting the scheduling technique to be "{technique}"')
		self.sched_tech = technique

	# function for setting the data dependency constraint between two nodes
	def set_data_dependency_constraints(self):
		'''
		if there is a forward dependency between node src and dst

		src -----> dst

		then we say the finishing time of sv_src must be eariler than the starting time of sv_dst
		sv_src + latency_src <= sv_dst

		'''
		for edge in get_cdfg_edges(self.cdfg): # Dependency constraint: per each edge
			if edge.attr['style'] != 'dashed':
				src, dst = self.cdfg.get_node(edge[0]), self.cdfg.get_node(edge[1])
				self.log.debug(f'Adding dependency constraint {src} -> {dst}')
				# sv_src >= sv_dst + latency; assume that the latency of each operation is 1 for now
				self.constraints.add_constraint({f'sv{src}' : -1, f'sv{dst}' : 1}, "geq", get_node_latency(src.attr) )


	# function for setting the initialization interval constraint from the back edges
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
			self.log.debug(f'Adding II constraint for backedge: {e[0]} -> {e[1]}')
			src, dst = self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1])
			assert src.attr['bbID'] == dst.attr['bbID'], 'sanity check failed: II defined only for single BB for now'
			# sv_src + latency_u <= sv_dst + II * Dist; if there is an back edge assume that for now the dependencies from the back edges all have dist = 1
			# TODO: determine the dependency distance?
			self.constraints.add_constraint({ f'sv{src}' : -1, f'sv{dst}' : 1, f'II_{src.attr["bbID"]}' : 1 }, "geq", get_node_latency(src.attr)) 

	# function to add max_latency constraint and optimization
	def add_max_latency_constraint(self):
		self.ilp.add_variable(f'max_latency', lower_bound = 0,  var_type="i")
		self.opt_fun.add_variable(f'max_latency', 1)

		ssinks = filter(lambda n : n.attr['type'] == 'supersink', get_cdfg_nodes(self.cdfg))
		for n in ssinks: # we try to minimize the latest SSINK
			self.constraints.add_constraint({f'sv{n}' : -1, f'max_latency' : 1}, "geq", 0)

	# function for setting the optimiztion funciton, according to the optimization option
	def set_opt_function(self):
		if self.sched_tech == 'no_pipeline':
			# ======================== Latency Minimization Objective ==========================#
			# objective: minimize the end-to-end latency
			self.add_max_latency_constraint()
		elif self.sched_tech == 'asap':
			# ======================== Latency Minimization per node Objective ==========================#
			# objective: minimize the end-to-end latency
			self.add_max_latency_constraint()

			for n in get_cdfg_nodes(self.cdfg): # we try to minimize all nodes delays
				self.opt_fun.add_variable(f'sv{n}', 1)
		elif self.sched_tech == 'alap':
			# ======================== Latency Maximization per node Objective ==========================#
			# objective: minimize the end-to-end latency
			self.add_max_latency_constraint()

			for n in get_cdfg_nodes(self.cdfg): # we try to minimize all nodes delays
				self.opt_fun.add_variable(f'sv{n}', -1)
		elif self.sched_tech == 'pipelined':
			# ======================== II Minimization Objective ===============================#
			self.ilp.add_variable(f'max_II', lower_bound = 0,  var_type="i")
			self.opt_fun.add_variable(f'max_II', 1)
			for bb in get_cdfg_nodes(self.cfg): # TODO: only minimize the II of the loop BB
				self.constraints.add_constraint({f'II_{bb}' : -1, 'max_II' : 1}, 'geq', 0)
		else:
			self.log.error(f'Not implemented option! {self.sched_tech}')
			raise NotImplementedError

	# function to create the ILP of the scheduling
	def create_scheduling_ilp(self):
		self.set_data_dependency_constraints()
		if self.sched_tech == "pipelined":
			self.set_II_constraints()
		self.set_opt_function()

	# function to solve the ilp and obtain scheduling
	def solve_scheduling_ilp(self, base_path, example_name):
		# log the result
		self.ilp.print_ilp("{0}/{1}/output.lp".format(base_path, example_name))
		res = self.ilp.solve_ilp()
		assert res == 1, "The ILP problem is unfeasible"
		self.sched_sol = self.ilp.get_ilp_solution()
		for var, value in self.ilp.get_ilp_solution().items():
			node_type = 'AUX'
			if re.search(r'^sv', var):
				node_name = re.sub(r'^sv', '', var)
				attributes = self.cdfg.get_node(node_name).attr
				node_type = attributes['type']
				attributes['label'] = attributes['label'] + '\n' + f'[{value}]'
			self.log.debug(f'{var} of type {node_type}:= {value}')
		self.cdfg.draw("test_dag_result.pdf", prog="dot")
		if 'max_latency' in self.ilp.get_ilp_solution():
			self.log.info(f'The maximum latency for this cdfg is {self.ilp.get_ilp_solution()["max_latency"]}')
		elif 'max_II' in self.ilp.get_ilp_solution():
			self.log.info(f'The maximum II for this cdfg is {self.ilp.get_ilp_solution()["max_II"]}')

	# function to get ilp, constraints and optimization function
	def get_ilp_tuple(self):
		return self.ilp, self.constraints, self.opt_fun

	# function to get the gantt chart of a scheduling 
	def print_gantt_chart(self):
		assert self.sched_sol != None, "There should be a solution to an ILP before running this function"
		print(self.sched_sol)