from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
import matplotlib.pyplot as plt
import re
import logging

# function to do sqrt in trivial way
def sqrt(n):
	i = 0
	while (i*i) < n:
		i+=1
	return i

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
#					- II : Initiation Interval achieved by scheduling solution
#					- log: logger object used to output logs
############################################################################################################################################
#	FUNCTIONS:
#					- set_sched_technique : set scheduling technique
#					- set_data_dependency_constraints: add data dependency constraints to the constraints
#					- set_II_constraints: add II constraints to the constraints
#					- add_max_latency_constraint : add max_latency constraint and optimization
#					- add_sink_delays_constraints : add sink delays constraints for alap (sink_delays should be a dictionary)
#					- set_opt_function: set optimization function according to the self.sched_tech
#					- create_scheduling_ilp : create the ILP of the scheduling
#					- solve_scheduling_ilp: run the solver on top of the constrants from set_*_constraints and the objective function from set_opt_function
#					- get_ilp_tuple : get ilp, constraints and optimization function
#					- get_sink_delays: get delays of sinks after computing solution (used by ALAP)
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
		self.II = None

		# set solver options
		self.ilp = ILP(log=log)
		self.constraints = Constraint_Set(self.ilp, log=log)
		self.opt_fun = Opt_Function(self.ilp, log=log)

		# remove all branch nodes, they force the II to be the same as iteration latency
		#self.cdfg.remove_nodes_from([ n for n in get_cdfg_nodes(self.cdfg) if n.attr['type'] == 'br' ]) 

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
	def set_data_dependency_constraints(self, break_bb_connections=False):
		'''
		if there is a forward dependency between node src and dst

		src -----> dst

		then we say the finishing time of sv_src must be eariler than the starting time of sv_dst
		sv_src + latency_src <= sv_dst

		'''
		for edge in get_cdfg_edges(self.cdfg): # Dependency constraint: per each edge
			if edge.attr['style'] != 'dashed':
				src, dst = self.cdfg.get_node(edge[0]), self.cdfg.get_node(edge[1])
				# if the break_bb_connections is set to True and the edge is between blocks of different BBs, the data dependency is ignored
				if break_bb_connections and src.attr['id'] != dst.attr['id']: 
					continue
				self.log.debug(f'Adding dependency constraint {src} -> {dst}')
				# sv_src >= sv_dst + latency; assume that the latency of each operation is 1 for now
				self.constraints.add_constraint({f'sv{src}' : -1, f'sv{dst}' : 1}, "geq", get_node_latency(src.attr) )


	# function for setting the initialization interval constraint from the back edges to the value II_value
	def set_II_constraints(self, II_value):
		assert self.sched_tech != 'no_pipeline', 'sanity check'
		# ===================== II Constraints ====================== #
		'''
		if there is a inter-iteration dependency between node n and v (which corresponds to a backedge)

		n -----> v

		then we say the finishing time of sv_n must be eariler than the starting time of sv_v
		sv_n + latency_n <= sv_v + II * dist_nv

		'''
		# define one II for the external loop
		self.ilp.add_variable(f'II', lower_bound = 1, var_type='i')
		self.constraints.add_constraint({f'II':1}, "eq", II_value) # constraint to set II to a certain value

		# cross-iteration constraint: per each backedge
		for e in get_back_edges(self.cdfg): 
			self.log.debug(f'Adding II constraint for backedge: {e[0]} -> {e[1]}')
			src, dst = self.cdfg.get_node(e[0]), self.cdfg.get_node(e[1])
			assert src.attr['bbID'] == dst.attr['bbID'], 'sanity check failed: II defined only for single BB for now'
			# sv_src + latency_u <= sv_dst + II * Dist; if there is an back edge assume that for now the dependencies from the back edges all have dist = 1
			# TODO: add memory dependency distance
			self.constraints.add_constraint({ f'sv{src}' : -1, f'sv{dst}' : 1, f'II' : 1 }, "geq", get_node_latency(src.attr)) 

	# function to add max_latency constraint and optimization
	def add_max_latency_constraint(self):
		self.ilp.add_variable(f'max_latency', lower_bound = 0,  var_type="i")
		self.opt_fun.add_variable(f'max_latency', 1)

		ssinks = filter(lambda n : n.attr['type'] == 'supersink', get_cdfg_nodes(self.cdfg))
		for n in ssinks: # we try to minimize the latest SSINK
			self.constraints.add_constraint({f'sv{n}' : -1, f'max_latency' : 1}, "geq", 0)

	# function to add sink delays constraints for alap (sink_delays should be a dictionary)
	def add_sink_delays_constraints(self, sink_delays):
		for sink in sink_delays:
			if not(sink in get_cdfg_nodes(self.cdfg)):
				self.log.error("The sink node {} does not belong to the cdfg".format(sink))
				continue
			self.constraints.add_constraint({"sv{}".format(sink) : 1}, "leq", sink_delays[sink])

	# function for setting the optimiztion funciton, according to the optimization option
	def set_opt_function(self):
		if self.sched_tech == 'no_pipeline':
			# ======================== Latency Minimization Objective ==========================#
			# objective: minimize the end-to-end latency
			self.add_max_latency_constraint()
		elif self.sched_tech == 'asap':
			# ======================== Latency Minimization per node Objective ==========================#
			# objective: minimize the end-to-end latency

			for n in get_cdfg_nodes(self.cdfg): # we try to minimize all nodes delays
				self.opt_fun.add_variable(f'sv{n}', 1)
		elif self.sched_tech == 'alap':
			# ======================== Latency Maximization per node Objective ==========================#
			# objective: minimize the end-to-end latency
		
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

	# function to create the ILP of the scheduling # sink delays corresponds to minimum delay of super_sinks using asap
	def create_scheduling_ilp(self, sink_delays=None):
		if self.sched_tech == "no_pipeline":
			self.set_data_dependency_constraints()
		elif self.sched_tech == "asap" or self.sched_tech == "alap":
			self.set_data_dependency_constraints(break_bb_connections=True)
			if self.sched_tech == "alap":
				assert sink_delays!= None and sink_delays != [], "ALAP scheduling needs the specification of sink delays as maximum allowed delay"
				self.add_sink_delays_constraints(sink_delays)
		elif self.sched_tech == "pipelined":
			self.set_II_constraints()
		self.set_opt_function()

	# function to solve the ilp and obtain scheduling
	def solve_scheduling_ilp(self, base_path, example_name):
		# log the result
		self.ilp.print_ilp("{0}/{1}/output.lp".format(base_path, example_name))
		res = self.ilp.solve_ilp()
		assert res == 1, "The ILP problem cannot be solved"
		self.sched_sol = self.ilp.get_ilp_solution() # save solution in an attribute
		# iterate through the different variables to obtain results
		for var, value in self.ilp.get_ilp_solution().items():
			node_type = 'AUX'
			# check if the node represents a timing
			if re.search(r'^sv', var):
				node_name = re.sub(r'^sv', '', var)
				attributes = self.cdfg.get_node(node_name).attr
				node_type = attributes['type']
				attributes['label'] = attributes['label'] + '\n' + f'[{value}]'
				attributes['latency'] = value
			self.log.debug(f'{var} of type {node_type}:= {value}')
		self.cdfg.draw("test_dag_result.pdf", prog="dot")
		if 'max_latency' in self.ilp.get_ilp_solution():
			self.log.info(f'The maximum latency for this cdfg is {self.ilp.get_ilp_solution()["max_latency"]}')
		elif 'max_II' in self.ilp.get_ilp_solution():
			self.log.info(f'The maximum II for this cdfg is {self.ilp.get_ilp_solution()["max_II"]}')
			self.II = self.ilp.get_ilp_solution()["max_II"]

	# function to get ilp, constraints and optimization function
	def get_ilp_tuple(self):
		return self.ilp, self.constraints, self.opt_fun

	# function to get delays of sinks after computing solution (used by ALAP)
	def get_sink_delays(self):
		assert self.sched_sol != None, "You need to run the solution before retrieving sink delays"
		output = {}
		for var, value in self.ilp.get_ilp_solution().items():
			# check if the node contains svssink word
			if re.search(r'^svssink', var):
				output[var.replace("sv","")] = value
		return output

	# function to get the gantt chart of a scheduling 
	def print_gantt_chart(self, chart_title="Untitled", file_path=None):
		assert self.sched_sol != None, "There should be a solution to an ILP before running this function"
		variables = {}
		start_time = {}
		duration = {}
		latest_tick = {} # variable to find last tick for xlables
		bars_colors = {}
		for node_name in get_cdfg_nodes(self.cdfg):
			if 'label' in self.cdfg.get_node(node_name).attr:
				attributes = self.cdfg.get_node(node_name).attr
				bb_id = attributes['id']
				if not(bb_id in variables):
					variables[bb_id] = []
					start_time[bb_id] = []
					duration[bb_id] = []
					bars_colors[bb_id] = []
					latest_tick[bb_id] = 0
				variables[bb_id].append(node_name)
				start_time[bb_id].append(float(attributes['latency'])) # start time of each operation
				node_latency = float(get_node_latency(attributes))
				if node_latency == 0.0:
					node_latency = 0.1
					bars_colors[bb_id].append("firebrick")
				else:
					bars_colors[bb_id].append("dodgerblue")
				duration[bb_id].append(node_latency) # duration of each operation
				tmp_tick = float(attributes['latency']) + float(get_node_latency(attributes))
				if tmp_tick > latest_tick[bb_id]:
					latest_tick[bb_id] = tmp_tick
		graphs_per_row = sqrt(len(variables))
		#fig, axs = plt.subplots(int(len(variables)))
		fig = plt.figure()
		axs=[]
		subplot_format = (graphs_per_row * 110) + 1

		axs_id = 0
		for bb_id in variables:
			axs.append(fig.add_subplot(subplot_format))
			subplot_format += 1
			axs[axs_id].barh(y=variables[bb_id], left=start_time[bb_id], width=duration[bb_id], color=bars_colors[bb_id])
			axs[axs_id].grid()
			axs[axs_id].set_xticks([i for i in range(int(latest_tick[bb_id])+1)])
			axs[axs_id].title.set_text("BB {}".format(bb_id))
			if self.II != None: # adding II information on the plot
				axs[axs_id].hlines(y=-1, xmin=0, xmax=self.II, color='r', linestyle = '-')
				axs[axs_id].text(self.II/2-0.35, -2, "II = {0}".format(int(self.II)), color='r')
			axs_id += 1
		#plt.title(chart_title)
		if file_path != None:
			plt.savefig(file_path)
		plt.show()