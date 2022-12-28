from src.utilities.ilp_manager import *

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
