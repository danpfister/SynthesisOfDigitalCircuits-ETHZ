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
		self.check_resource_dict(resource_dict)

		#output to terminal that this is the next function to implement
		self.log.error("The add_resource_constraints member function in src/main_flow/resources.py has not yet been implemented")
		self.log.info("Exiting early due to an unimplemented function")

		quit()

	# function to add resources constraints for pipelined scheduling
	def check_resource_constraints_pipelined(self, resource_dict, II):
		self.check_resource_dict(resource_dict)

		#output to terminal that this is the next function to implement
		self.log.error("The check_resource_constraints_pipelined member function in src/main_flow/resources.py has not yet been implemented")
		self.log.info("Exiting early due to an unimplemented function")
		quit()


	"""
	Checks the types specified in the given resource dictionary(a dictionary containing something like "bogusoperationtype" wouldn't be valid) and sets the resource_dic member variable of the class to the specified resource dictionary
	@param resource_dic: the resource dictionary that the class should use
	"""
	def check_resource_dict(self, resource_dict):
		for resource in resource_dict:
			if not(resource in allowed_resources): # the resource type should be present in the list of allowed resource types
				self.log.error("Resource {0} is not allowed (allowed resources = {1})".format(resource, allowed_resources))
				continue