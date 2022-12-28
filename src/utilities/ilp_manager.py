import pulp as ilp

############################################################################################################################################
############################################################################################################################################
#
#	`OPT_FUNCTION` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#				 The following class is used to describe the optimization function of the ILP formulation
############################################################################################################################################
#	ATTRIBUTES:
#				- valid : validity of the optimizaiton function
#				- function_coeff : output optimization function with coefficients
#				- ilp_obj : ILP object linked to optimization function
############################################################################################################################################
#	FUNCTIONS:
#				- is_valid : returns the validity of the optimization function
#				- add_variable : add variable and corresponding coefficient in the optimization function
#				- remove_variable : remove variable in the optimization function
#				- get_opt_function : get optimization function
############################################################################################################################################
############################################################################################################################################

class Opt_Function:

	def __init__(self, ilp_obj, coeff_dict = None):
		assert(ilp_obj != None) # ilp_obj represents the ILP object to which the optimization function belongs to
		self.valid = True
		self.function_coeff = {}
		self.ilp_obj = ilp_obj
		ilp_obj.set_optimization_function(self)
		if coeff_dict == None: # the coefficients can be added later on
			return
		var_list = ilp_obj.get_variables_list() # if the coefficient dictionary is different from None, it is used to generate the first 
		for var in coeff_dict:
			if not(var in var_list):
				print("[ERROR] {0} is not a variable in the ILP object".format(var))
				self.valid = False
				return
		self.function_coeff = coeff_dict	

	# function to return validity of the optimization function
	def is_valid(self):
		return self.valid

	# function to add a new variable and its corresponding coefficient in the optimization function
	def add_variable(self, var_name, coeff=1):
		if not(self.valid):
			print("[ERROR] Opt_Function object is not valid!")
			return
		if not(var_name in self.ilp_obj.get_variables_list()):
			print("[ERROR] Variable not present in the ILP object")
			return
		if not(str(coeff).isnumeric()):
			print("[ERROR] Coefficient {0} is not numeric!".format(coeff))
			return
		if var_name in self.function_coeff:
			print("[WARNING] The variable {0} is already present in the optimization function.".format(var_name))
			print("Old coefficient : {1}\nNew Coefficient : {2}".format(self.function_coeff[var_name], coeff))
		self.function_coeff[self.ilp_obj.get_variable(var_name)] = coeff
	
	# function to remove a variable from the optimization function
	def remove_variable(self, var_name):
		assert(var_name in self.function_coeff)
		del self.function_coeff[var_name]

	# function to get the optimization function
	def get_opt_function(self):
		return ilp.LpAffineExpression(e=self.function_coeff)


############################################################################################################################################
############################################################################################################################################
#
#	`CONSTRAINT_SET` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#				 The following class is used to describe the constraints of the ILP formulation
############################################################################################################################################
#	INFO:
#				'disequality_signs' is a dictionary that contains allowed signs for constraints
############################################################################################################################################
#	ATTRIBUTES:
#				- ilp_obj : ILP object linked to optimization function
#				- constraints : set of constraints
############################################################################################################################################
#	FUNCTIONS:
#				- add_constraint : add contraint to constraints' set
#				- remove_constraint : remove constraint from constraints
#				- get_constraints : retrieve constraints' set
############################################################################################################################################
############################################################################################################################################

disequality_signs = {"eq":0, "geq":1, "leq":-1}

class Constraint_Set:

	def __init__(self, ilp_obj):
		assert(ilp_obj != None) # ilp_obj represents the ILP object to which the optimization function belongs to
		self.constraints = {}
		self.ilp_obj = ilp_obj
		ilp_obj.set_constraints(self)

	# function to add a new constraint
	def add_constraint(self, coeff_list, dis_sign, right_constant=0):
		constraint_id = "c{0}".format(len(self.constraints) + 1)
		constraint = {}
		for var_name in coeff_list:
			if not(type(var_name) is str):
				print("[ERROR] Variable {0} should be a string (the name of the variable)".format(var_name))
				return None
			if not(var_name in self.ilp_obj.get_variables_list()):
				print("[ERROR] Variable {0} not present in the ILP object".format(var_name))
				return None
			if not(dis_sign in disequality_signs):
				print("[ERROR] Disequality sign {0} is not allowerd. Allowed signs = {1}".format(dis_sign, disequality_signs.keys()))
				return None
			coefficient = coeff_list[var_name]
			if not(str(coefficient).isnumeric()):
				print("[ERROR] Coefficient {0} of variable {1} is not numeric".format(coeff_list[var_name], var_name))
				return None
			if not(str(right_constant).isnumeric()):
				print("[ERROR] Right Coefficient of the constraint {0} is not numeric".format(right_constant))
				return None
			# the constraint is a dictionary with variables as keys and coefficients as values
			constraint[self.ilp_obj.get_variable(var_name)] = coefficient
		# generation of constraint using the LpConstraint object
		constraint = ilp.LpConstraint(e=ilp.LpAffineExpression(e=constraint), sense=disequality_signs[dis_sign], name=constraint_id ,rhs=right_constant)
		self.constraints[constraint_id] = constraint
		return constraint_id
	
	# function to remove a constraint
	def remove_constraint(self, constraint_id):
		assert(constraint_id in self.constraints)
		del self.constraints[constraint_id]

	# function to retrieve constraints
	def get_constraints(self):
		return self.constraints

############################################################################################################################################
############################################################################################################################################
#
#	`ILP` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#				 The following class is used to interact with the ILP formulation
############################################################################################################################################
#	ATTRIBUTES:
#				- solver : ILP solver
#				- model_name : name of the ILP model
#				- model_minimize : model objective function should be minimized or maximized
#				- model : ILP model
#				- variables : ILP variables
#				- opt_function : optimization function
#				- constraints : constraints set
#				- status : status of the ILP solution
############################################################################################################################################
#	FUNCTIONS:
#				- set_solver : set the ILP solver
#				- get_solver : get the ILP solver
#				- add_variable : add an ILP variable
#				- remove_variable : remove an ILP variable
#				- get_variable : get a variable
#				- get_variables_list : get the list of variables
#				- set_optimization_function : set the optimization function
#				- update_model : update the model with a constraint set and an optimization function
#				- solve_ilp	: solve the ILP formulation
#				- print_ilp : print the ILP formulation
#				- get_ilp_solution : get ILP solution
############################################################################################################################################
############################################################################################################################################


class ILP:

	def __init__(self, solver="PULP_CBC_CMD", minimize=True):
		self.set_solver(solver)
		self.model_name = "ILP_model"
		self.model_minimize = minimize
		if minimize:
			self.model = ilp.LpProblem(self.model_name, ilp.LpMinimize)
		else:
			self.model = ilp.LpProblem(self.model_name, ilp.LpMaximize)
		self.variables = {}
		self.constraints = None
		self.opt_function = None
		self.status = None

	# function to set the solver
	def set_solver(self, solver="PULP_CBC_CMD"):
		list_solvers = ilp.listSolvers()
		assert(solver in list_solvers) #check that the solver is in the solver list
		self.solver = solver

	# function to get the solver
	def get_solver(self):
		return self.solver
	
	# function to add an ILP variable
	def add_variable(self, var_name, lower_bound = None, upper_bound = None, var_type = 'c'):
		assert(not(var_name in self.variables)) # check that var_name is not in the list of variables
		assert(str(upper_bound).isnumeric() or upper_bound == None) # assert that upper bound is numeric or None
		assert(str(lower_bound).isnumeric() or lower_bound == None) # assert that lower bound is numeric or None
		var_type_dic = {'i':"Integer", 'b': "Binary", 'c':"Continuous"} # dictionary to associate char to var_type
		if not(var_type in var_type_dic):
			print("[ERROR] ILP variable has only 3 var_type: i(nteger), b(inary) and c(continuous)")
			return
		var = ilp.LpVariable(var_name, upper_bound, lower_bound, var_type_dic[var_type])
		self.variables[var_name] = var
	
	# function to remove an ILP variable
	def remove_variable(self, var_name):
		assert(var_name in self.variables) # check that the variable is in the list of variables
		del self.variables[var_name]

	# function to get a variable
	def get_variable(self, var_name):
		assert(var_name in self.variables) # the var_name should be in the dictionary of variables
		return self.variables[var_name]

	# function to retrieve variables
	def get_variables_list(self):
		return self.variables

	# function to set optimization function
	def set_optimization_function(self, opt_function):
		if not(type(opt_function) is Opt_Function): # check that the optimization function is an object of the class Opt_Function
			print("[ERROR] Optimization Function needs to be object of the class Opt_Function")
			return 
		self.opt_function = opt_function

	# function to set constraints' set
	def set_constraints(self, constraints):
		if not(type(constraints) is Constraint_Set): # check that the constraints is an object of the class Constraint_Set
			print("[ERROR] Constraints need to be object of the class Constraint_Set")
			return 
		self.constraints = constraints

	# function to update the model with a constraint set and an optimization function
	def update_model(self, model, constraints_set, opt_function):
		assert(not(model is None)) # check that model is not None
		assert(not(constraints_set is None)) # check that constraints' set is not None
		assert(not(opt_function is None) and opt_function.is_valid()) # check the optimization function is not None and the optimization function is valid
		constraints = constraints_set.get_constraints()
		for constraint_id in constraints:
			model += constraints[constraint_id] , constraint_id # adding contraint in the model
		model += opt_function.get_opt_function(), "Objective_Function" # adding optimization function in the model
		return model

	# function to solve the ILP formulation
	def solve_ilp(self):
		self.model = self.update_model(self.model, self.constraints, self.opt_function)
		solver = ilp.getSolver(self.get_solver(), msg=0) # msg=0 enforces no output of the ILP solver
		self.status = self.model.solve(solver)
		if(self.status != 1):
			print("[WARNING] ILP problem is unfeasible")
		return self.status

	# function to print the ILP formulation
	def print_ilp(self, output_file="output.lp"):
		if self.model_minimize:
			model = ilp.LpProblem(self.model_name, ilp.LpMinimize)
		else:
			model = ilp.LpProblem(self.model_name, ilp.LpMaximize)
		model = self.update_model(model, self.constraints, self.opt_function)
		model.writeLP(output_file)
		print("[Info] The ILP formulation is written in "+output_file)

	# function to get ILP solution
	def get_ilp_solution(self):
		assert self.status != None and self.status == 1, "The function `solve_ilp` has to be called before using `get_ilp_solution` and its result has to be valid" # check that the ILP solution is valid
		result = {}
		for var_name in self.variables:
			result[var_name] = self.variables[var_name].varValue
		return result