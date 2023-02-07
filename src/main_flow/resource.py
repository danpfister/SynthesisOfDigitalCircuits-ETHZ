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
#					- is_legal : it checks if the MRT is legal
############################################################################################################################################
############################################################################################################################################

class MRT: # Modulo Reservation Table (MRT)
	def __init__(self, ilp):
		self.generate(ilp)

	# function to generate the MRT
	def generate(self, ilp):
		# TODO: write your code here
		pass

	# function to check legal MRT
	def is_legal(self, operation, clock_time, max_allowed_instances, operations_solved):
		# TODO: write your code here
		pass


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
# 					- add_resource_constraints : setting up the maximum resource usage per res type in the constraint set
#					- add_resource_constraints_pipelined : add resources constraints for pipelined scheduling
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

	# function for setting up the maximum resource usage per res type in the constraint set
	def add_resource_constraints(self, ilp, constraints, opt_function):
		self.set_ilp_tuple(ilp, constraints, opt_function)
		# TODO: write your code here
		pass

	# function to add resources constraints for pipelined scheduling
	def add_resource_constraints_pipelined(self, ilp, constraints, opt_function, budget):
		self.set_ilp_tuple(ilp, constraints, opt_function)
		# TODO: write your code here
		pass