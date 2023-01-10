from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
import logging

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
# 					- add_resource_constraints : add resource dependency constraints to the constraints set
############################################################################################################################################
############################################################################################################################################

allowed_resources = ["load", "add"]

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

	# function for setting up the maximum resource usage per res type in the constraint set
	def add_resource_constraints(self, ilp, constraints, opt_function):
		self.set_ilp_tuple(ilp, constraints, opt_function)
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