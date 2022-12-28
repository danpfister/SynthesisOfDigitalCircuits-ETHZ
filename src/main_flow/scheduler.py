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
#					- 
############################################################################################################################################
#	FUNCTIONS:
#					- 
############################################################################################################################################
############################################################################################################################################

class Scheduler:

    def __init__(self):
        pass

    def test(self, base_path, example_name):
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
