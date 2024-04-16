from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
import logging

############################################################################################################################################
############################################################################################################################################
#
#	`RESOURCE_MANAGER` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#					The following class is used for resource sharing in CDFG (Control DataFlow Graph) representing a function.
############################################################################################################################################
#	ATTRIBUTES:
#					- ilp : ILP problem of the class ILP
#					- constraint_set : set of constraints of the class CONSTRAINT_SET
#					- obj_function : optimization function of the class Obj_Function
#					- log: logger object used to output logs
############################################################################################################################################
#	FUNCTIONS:
# 					- add_resource_constraints : setting up the maximum resource usage per res type in the constraint set
#					- add_resource_constraints_pipelined : add resources constraints for pipelined scheduling
#					- check_resource_dict : validate values in resource dict
############################################################################################################################################
############################################################################################################################################

allowed_resources = ["load", "add", "mul", "div", "zext"]

class Resource_Manager:
	def __init__(self, parser, ilp_dependency_inj, log=None, ):
		assert(parser != None) # ensure Parser is different from None
		assert(ilp_dependency_inj != None) # ensure ilp source is different from None
		self.cdfg = parser.get_cdfg() # save the CDFG of the parser
		self.cfg = parser.get_cfg() # save the CFG of the parser
		if log != None:
			self.log = log
		else:
			self.log = logging.getLogger('resource') # if the logger is not given at object generation, create a new one
		
		ilp_dependency_inj(self)

	"""
	Adds scheduling ILP created by the Scheduler must be passed to the Resources
	"""
	def set_scheduling_ilp(self, ilp, constraints, obj_fun):
		self.ilp = ilp
		self.constraints = constraints
		self.obj_fun = obj_fun


	"""
	Adds constraints to the constraint set that enforce the resource constraints contained in the resource dictionary
	"""
	def add_resource_constraints(self, resource_dict):
		self.check_resource_dict(resource_dict) # dict e.g.: {'add': 1, 'mul': 1, 'zext': 1}

		ordered_instructions = get_topological_order(self.cdfg) #TODO: need to probably adjust sorting here
		instruction_exec_time = {'add': 1, 'mul': 4}

		# dict containing the ordered nodes of each constrained resource
		constrained_instructions = {instr_type: [] for instr_type in resource_dict.keys()}
		for instruction in ordered_instructions:
			instr_type = instruction.attr["type"]
			if instr_type not in constrained_instructions.keys(): continue # not resource constrained
			self.log.debug(f"instruction {instruction} has type {instr_type}")
			constrained_instructions[instr_type] = constrained_instructions[instr_type] + [instruction]
		self.log.debug(constrained_instructions)

		# add constraint for each constrained resource
		for instr_type, nodes in constrained_instructions.items():
			last_timestep_node = "ssrc_0" #TODO hardcoded for now
			current_timestep_node = None
			resource_load = 0
			for node in nodes:
				if resource_load == resource_dict[instr_type]: # check if maximum resource load is reached
					last_timestep_node = current_timestep_node
					resource_load = 0
				current_timestep_node = node
				resource_load += 1
				self.log.debug(f"adding constraint sv{node} - sv{last_timestep_node} >= 1")
				self.constraints.add_constraint({f"sv{last_timestep_node}": -1, f"sv{node}": 1}, "geq", instruction_exec_time.get(instr_type, 1))
					
		"""
		given a resource R constrained with C:
		start first C operations as early as possible
		start next C operations after completion of the first C operations
		and so on
		"""


		#output to terminal that this is the next function to implement
		#self.log.error("The add_resource_constraints member function in src/main_flow/resources.py has not yet been implemented")
		#self.log.info("Exiting early due to an unimplemented function")

		#quit()

	'''
	return true if MRT construction succeeds, else false
	'''
	def check_resource_constraints_pipelined(self, resource_dict, II):
		self.check_resource_dict(resource_dict)

		#output to terminal that this is the next function to implement
		#self.log.error("The check_resource_constraints_pipelined member function in src/main_flow/resources.py has not yet been implemented")
		#self.log.info("Exiting early due to an unimplemented function")

		MRT_dictionary = dict()
		for node in self.cdfg:
			node_timing = self.ilp.get_operation_timing_solution(node)
			column_index = int(node_timing % II)
			if column_index in MRT_dictionary.keys():
				MRT_dictionary[column_index] = MRT_dictionary[column_index] + [node.attr["type"]]
			else:
				MRT_dictionary[column_index] = [node.attr["type"]]

		self.log.debug(f"checking {MRT_dictionary} with {resource_dict}")

		for column_index, resource_list in MRT_dictionary.items():
			for resource_type, resource_number in resource_dict.items():
				if resource_list.count(resource_type) > resource_number:
					return False
		return True
		
		#quit()


	"""
	Checks the types specified in the given resource dictionary(a dictionary containing something like "bogusoperationtype" wouldn't be valid) and sets the resource_dic member variable of the class to the specified resource dictionary
	@param resource_dic: the resource dictionary that the class should use
	"""
	def check_resource_dict(self, resource_dict):
		for resource in resource_dict:
			if not(resource in allowed_resources): # the resource type should be present in the list of allowed resource types
				self.log.error("Resource {0} is not allowed (allowed resources = {1})".format(resource, allowed_resources))
				continue