from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
import logging

############################################################################################################################################
############################################################################################################################################
#
#	`MRT` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#					The following class is used for the Modulo Reservation Table (MRT) for resource sharing in pipelined SDC
############################################################################################################################################
#	ATTRIBUTES:
#					- mrt : is the MRT dictionary where the keys are the clock cycles and the values are lists of operations
############################################################################################################################################
#	FUNCTIONS:
#					- generate : it generates the MRT for a given ILP solution
#					- is_legal : it checks if the presence of an operation at a given clock respects the resources constraint
############################################################################################################################################
############################################################################################################################################

class MRT: # Modulo Reservation Table (MRT)
	def __init__(self, ilp):
		self.generate(ilp)

	# function to generate the MRT
	def generate(self, ilp):
		'''
		Generate Modulo Reservation Table to plot the pipelined scheduling of a given ilp solution

		II <- ilp.get_II()
		max_latency <- ilp.get_maxLatency()
		
		output_dictionary <- {}
		for clock in max_latency: 												# iterate until max_latency
			operations_clock <- ilp.get_operations(clock) 						# operations of first iteration
			number_overlapping_iterations <- clock/II 							# number of overlapping iterations at step clock
			for iteration_number in (1, number_overlapping_iterations):			# iterate through overlapping iterations
				clock_iteration <- clock - II*iteration_number 					# clock wrt iteration iteration_number
				operations_overlapping <- ilp.get_operations(clock_iteration)	# get operations in overlapping iteration iteration_number
				operations_clock.extend(operations_overlapping)					# updating the total number of operations
			output_dictionary[clock] = operations_clock
		return output_dictionary

		'''
		II = ilp.get_II_solution()
		max_latency = int(ilp.get_max_latency_solution())
		self.mrt = {}
		for clock in range(max_latency):
			operations_clock = ilp.get_variables_solution(clock)
			number_overlapping_iterations = int(clock/II)
			for iteration_number in range(1, number_overlapping_iterations+1):
				clock_iteration = clock - (II * iteration_number)
				operations_overlapping = ilp.get_variables_solution(clock_iteration)
				operations_clock.extend(operations_overlapping)
			self.mrt[clock] = operations_clock
		return self.mrt

	# function to check legal MRT
	def is_legal(self, operation, clock_time, max_allowed_instances, operations_solved):
		'''
		Check if the number of operations of type operation respects the resource constraint (of max_allowed_instances) given the operations for which the time has been set already (operations_solved)
		'''
		list_operations = self.mrt[clock_time]
		assert operation in list_operations, "The operation considered ({operation}) should be present in the operation list ({list_operations}) for clock {clock_time}"
		cnt_operations = 0
		for op in list_operations: # check if in the list of operations happening in one clock exceed the maximum number of operations 
			if op in operations_solved or op == operation:
				cnt_operations += 1
		if cnt_operations > max_allowed_instances:
			return False
		else:
			return True


############################################################################################################################################
############################################################################################################################################
#
#	`RESOURCE` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#					The following class is used for resource sharing in CDFG (Control DataFlow Graph) representing a function.
############################################################################################################################################
#	ATTRIBUTES:
#					- resource_dic : dictionary containing resources
#					- ilp : ILP problem of the class ILP
#					- constraint_set : set of constraints of the class CONSTRAINT_SET
#					- opt_function : optimization function of the class OPT_FUNCTION
#					- log: logger object used to output logs
############################################################################################################################################
#	FUNCTIONS:
#					- set_ilp_tuple : set ilp, constraints and optimization function
#					- set_resource_constraints : set resource constraints
# 					- add_resource_constraints_sdc : add resource dependency constraints to the constraints set (following SDC approach)
# 					- add_resource_constraints_deMicheli : add resource dependency constraints to the constraints set (following De Micheli approach)
############################################################################################################################################
############################################################################################################################################

allowed_resources = ["load", "add", "mul", "div", "zext"]

class Resources:
	def __init__(self, parser, resource_dic=None, log=None):
		assert(parser != None) # ensure Parser is different from None
		self.cdfg = parser.get_cdfg() # save the CDFG of the parser
		self.cfg = parser.get_cfg() # save the CFG of the parser
		if log != None:
			self.log = log
		else:
			self.log = logging.getLogger('resource') # if the logger is not given at object generation, create a new one
		self.resource_dic = {}
		if resource_dic != None:
			self.set_resource_constraints(resource_dic)
		self.ilp = None
		self.constraint_set = None
		self.opt_function = None

	# function to set ilp, constraints and optimization function
	def set_ilp_tuple(self, ilp, constraint_set, opt_function):
		if ilp == None:
			self.ilp = ILP(log=self.log)
		else:
			self.ilp = ilp
		self.constraint_set = constraint_set
		self.opt_function = opt_function

	#function to set the resource constraints using a dictionary input
	def set_resource_constraints(self, resource_dic):
		for resource in resource_dic:
			if not(resource in allowed_resources): # the resource type should be present in the list of allowed resource types
				self.log.error("Resource {0} is not allowed (allowed resources = {1})".format(resource, allowed_resources))
				continue
			if resource in self.resource_dic:
				self.log.warning("Resource {0} is already present in the dictionary. \n\tOld value = {1} New value = {2}".format(resource, self.resource_dic[resource], resource_dic[resource]))
			self.resource_dic[resource] = resource_dic[resource]

	# function for setting up the maximum resource usage per res type in the constraint set (following SDC approach)
	def add_resource_constraints_sdc(self, ilp, constraints, opt_function):
		self.set_ilp_tuple(ilp, constraints, opt_function)
		""" 
		SDC APPROACH
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
		self.log.debug(f'Topological ordering: {topological_order}')
		# assume the following resource constraints:
		# load port <= 2; adders <= 1;
		#resource_constraint = { 'load' : 2, 'add' : 1 }

		# resource constraints are done within each BB
		for bb in get_cdfg_nodes(self.cfg):
			for resource_type, max_instances in self.resource_dic.items():
				self.log.debug(f'Adding resource constraint: {resource_type} has maximum of {max_instances} inside BB {bb}')
				# get all the nodes that have resource type resource_type inside the bb
				resources_ordered = [ n for n in topological_order
					if self.cdfg.get_node(n).attr['type'] == resource_type and self.cdfg.get_node(n).attr['bbID'] == bb ]
				self.log.debug(f'Nodes of type {resource_type} in BB {bb}: {resources_ordered}')
				# (2), (3): for each pair of nodes that have (RESOURCE - 1) nodes in between
				for i in range(len(resources_ordered)):
					resource_node_x = resources_ordered[i]
					try:
						resource_node_y = resources_ordered[ i + max_instances ]
					except IndexError:
						continue
					'''
					resource_node_x dominates resource_node_y in topological order, and there are already RESOURCE number of operations before resource_node_y
					
					'''
					self.log.debug(f'resource constraint between {resource_node_x} and {resource_node_y}')
					# (4): add constraint
					self.constraint_set.add_constraint({f'sv{resource_node_x}' : -1, f'sv{resource_node_y}' : 1}, "geq", get_node_latency(resource_node_x.attr) )

	# function for setting up the maximum resource usage per res type in the constraint set (following De Micheli approach)
	def add_resource_constraints_deMicheli(self, ilp, constraints, opt_function, sink_delays):
		self.set_ilp_tuple(ilp, constraints, opt_function)
		'''
		De Micheli approach
		There is a constraint per each clock which enforces the maximum number of constraint to respect the resource maximum. To use this type
		of resource constraint it is necessary to specify the maximum allowed clock constraint since the previous resource constraint should be
		limited by an integer value. 

		We introduce new variables describing the presence of a node in a specific time unit. x(i,t) is a binary value representing the presence
		of node i in timestamp t.
		Given two nodes i and j which use the same resource the following resource constraint is used:

		(1) x(i,t) + x(j,t) <= MAX_RESOURCES
		
		where (2) sv_i => x(i,t) * t					

		To ensure that a solution is found we have to include the following constraint per each sink

		(3) svssink_x <= sink_delay(sink_x)

		Also, to ensure that a solution is found we have to enforce that for every node type i only one x(i,t) is set to 1 for t in (0,T) where 
		T is the delay of the sink

		(4) sum(for t in [0,T]) x(i,t) = 1 

		'''

		# resource constraints are done within each BB
		for bb in get_cdfg_nodes(self.cfg):
			bb_id = self.cfg.get_node(bb).attr['id']
			sink_name = "ssink_"+str(bb_id)
			sink_delay = sink_delays[sink_name]
			for resource_type, max_instances in self.resource_dic.items():
				# get all the nodes that have resource type resource_type inside the bb
				resources = [ n for n in get_cdfg_nodes(self.cdfg)
					if self.cdfg.get_node(n).attr['type'] == resource_type and self.cdfg.get_node(n).attr['bbID'] == bb ]
				if len(resources) <= max_instances:
					continue # if the number of resources in the BB does not exceed the maximum allowed, the BB can be skipped
				self.log.debug(f'Adding resource constraint: {resource_type} has maximum of {max_instances} inside BB {bb}')
				self.log.debug(f'Nodes of type {resource_type} in BB {bb}: {resources}')
				# iterating along the sink_delay slack to define each x(i,t) variable and the constraint 
				for time_stamp in range(1, int(sink_delay)+1): #TODO: consider the case in which start point is different from 0
					resource_constraint = {}
					for res in resources:
						x_variable = "x_{0}_{1}".format(time_stamp, res)
						self.ilp.add_variable("x_{0}_{1}".format(time_stamp, res), var_type='b') # creating the x_variable
						self.constraint_set.add_constraint({"sv{}".format(res) : 1, x_variable : -time_stamp}, "geq", 0) # disequality (2)
						resource_constraint[x_variable] = 1
					self.constraint_set.add_constraint(resource_constraint, "leq", max_instances) # disequality (1), per each timestamp
				for res in resources:
					resource_constraint = {}	
					for time_stamp in range(1, int(sink_delay)+1): #TODO: consider the case in which start point is different from 0
						x_variable = "x_{0}_{1}".format(time_stamp, res)		
						resource_constraint[x_variable] = 1
					self.constraint_set.add_constraint(resource_constraint, "eq", 1) # desaquality (4) for each resource type
				
			self.constraint_set.add_constraint({"sv"+sink_name : 1}, "leq", sink_delay)




	# function to add resources constraints for pipelined scheduling
	def add_resource_constraints_pipelined(self, ilp, constraints, opt_function, budget):
		self.set_ilp_tuple(ilp, constraints, opt_function)
		'''
		Given an initial SDC scheduling, each operation using a specific resource is checked to respect a resource constraint. 

		schedQueue : initial queue containing all resource constrained operations

		budget : maximum allowed number of iterations

		ILP : ILP object which contains sdcSolution

		sdcSolution : solution of previous SDC run

		II : II used for sdcSolution

		operations_solved : list of operations for which clock time has been decided

		constraint_list : list of new constraints added and to remove in case of failure

		MRT <- MRT(ILP)
		operations_solved <- []
		constraint_list <- []
		while schedQueue not empty and budget >= 0 then
			operation <- pop schedQueue
			sv_operation <- ILP.get_operation_timing_solution(operation)
			if is_MRT_legal(MRT, operation, sv_operation) then
				constraint_id <- constraints.add(operation_time = sv_operation)
				constraint_list.append(constraint_id)
				MRT.generate(ILP)
				operations_solved.append(operation)
			else
				constraint_id <- constraints.add(operation_time >= sv_operation + 1)
				constraint_list.append(constraint_id)
				status = ilp.solve()
				if status is feasible then
					schedQueue <- push schedQueue operation
				else
					ilp.remove_constraints(constraint_list)
					return Fail
			budget <- budget - 1
		if schedQueue not empty then
			return Fail
		else
			return Success

		'''

		mrt = MRT(self.ilp) # generate the first MRT for a given ILP solution
		constraint_list = []
		topological_order = get_topological_order(self.cdfg) # the topological_order is chosen as order of selection of resources
		sdc_solution_order = []
		for clock in range(int(self.ilp.get_max_latency_solution())):
			sdc_solution_order.extend(self.ilp.get_variables_solution(float(clock)))
		for resource_type, max_instances in self.resource_dic.items(): # multiple resource constrained can be specified
			# generating the list of operations of a specific resource constrained type
			schedQueue = [ n for n in topological_order if self.cdfg.get_node(n).attr['type'] == resource_type] 
			budget_res = budget
			operations_solved = []
			maximum_latency = self.ilp.get_max_latency_solution()
			while len(schedQueue) > 0 and budget_res >= 0:
				operation = schedQueue[0]
				schedQueue.remove(operation)
				sv_operation = self.ilp.get_operation_timing_solution(operation) # for the selected operation check the timing value according to SDC
				# check if for this clock and for the operations considered until now the resource constrained is respected
				if mrt.is_legal(operation, sv_operation, max_instances ,operations_solved):
					# the resource constraint is respected and the operation is enforced to a specific clock cycle
					c_id = self.constraint_set.add_constraint({f'sv{operation}':1},"eq",sv_operation)
					constraint_list.append(c_id)
					operations_solved.append(operation)
					self.log.debug("Operation {operation} has been set in clock {sv_operation}")
				else:
					if (sv_operation+1) > maximum_latency: # if the operation has been pushed too forward over the maximum latency
						for c_id in constraint_list: # then the constraints added are removed
							self.constraint_set.remove_constraint(c_id)
						return -1 # fail since the given II cannot accomplish the result wanted
					# the resource constraint is not respected and the operation is pushed of a new clock 
					c_id = self.constraint_set.add_constraint({f'sv{operation}':1},"geq", (sv_operation+1) )
					constraint_list.append(c_id)
					status = self.ilp.solve_ilp()
					if status == 1: # the SDC is feasible
						# the operation is gonna be analyzed for the following clock cycle
						schedQueue.insert(0, operation)
						mrt.generate(self.ilp)
					else:
						# the SDC is unfeasible (it could be because of datapath constraints or II constraints)
						for c_id in constraint_list:
							self.constraint_set.remove_constraint(c_id)
						return -1 # fail
				budget_res -= 1
			if len(schedQueue) > 0:
				return -1 # fail
			else:
				return 1 # success
