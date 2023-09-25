#!/usr/bin/env python3
import argparse
from src.main_flow.parser import Parser
from src.main_flow.scheduler import Scheduler
from src.main_flow.resource import Resource_Manager
import logging

# create log interface
log = logging.getLogger('sdc')
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler() # create console handler and set level to debug
formatter = logging.Formatter('%(levelname)s - %(message)s') # create formatter
console_handler.setFormatter(formatter) # add formatter to console
log.addHandler(console_handler) # add console_handler to log

def main(args):
	frontend_only = args.frontend
	input_list = args.input_list
	base_path = args.examples_folder
	debug_mode = args.debug


	log.info("Arguments selected:\n\tINPUT LIST = {0}\n\tEXAMPLE FOLDER PATH = {1}\n\tONLY FRONTEND = {2}\n\tDEBUG = {3} technique(s) = {4}".format(input_list, base_path, frontend_only, debug_mode, args.methods))

	# if debug_mode is selected logger is set to debug
	if debug_mode:
		log.setLevel(logging.DEBUG)

	#reading the list of examples to execute
	examples_list_file = open(input_list, "r")
	examples_list = examples_list_file.read().split("\n")
	examples_list_file.close()

	allowed_techniques = ["asap", "alap", "asap_rconst", "pipelined", "pipelined_rconst", "all"]
	if args.methods != None:
		techniques = args.methods.split()
		for t in techniques:
			if t not in allowed_techniques:
				error(f"{t} is not a valid scheduling method")
				error(f"allowed methods are {allowed_techniques}")
				return False
	else:
		techniques = allowed_techniques

	for example_name in examples_list:
		if example_name == "":
			continue

		for scheduling_type in techniques:

			log.info("*** BENCHMARK {0} ***".format(example_name))
			# the path of the ssa file should be base_path/example_name/reports/example_name.cpp_mem2reg_constprop_simplifycfg_die.ll
			path_ssa_example = "{0}/{1}/reports/{1}.cpp_mem2reg_constprop_simplifycfg_die.ll".format(base_path, example_name)

			log.info("Parsing file {0}".format(path_ssa_example))
			ssa_parser = Parser(path_ssa_example, example_name, log)
			if not(ssa_parser.is_valid()):
				log.error("Parser has encountered a problem. Please verify path correctness ({0})".format(path_ssa_example))
				continue
			ssa_parser.draw_cdfg("{0}/{1}/test.pdf".format(base_path, example_name))

			if scheduling_type == "asap":
				asap(ssa_parser, base_path, example_name)

			elif scheduling_type == "alap":
				alap(ssa_parser, base_path, example_name)

			elif scheduling_type == "asap_rconst":
				asap_rconstrained(ssa_parser, base_path, example_name)

			elif scheduling_type == "pipelined":
				pipelined(ssa_parser, base_path, example_name)

			elif scheduling_type == "pipelined_rconst":
				pipelined_rconstrained(ssa_parser, base_path, example_name)

			elif scheduling_type == "all":
				asap(ssa_parser, base_path, example_name)
				alap(ssa_parser, base_path, example_name)
				asap_rconstrained(ssa_parser, base_path, example_name)
				pipelined(ssa_parser, base_path, example_name)
				pipelined_rconstrained(ssa_parser, base_path, example_name)

			else:
				print(f"{scheduling_type} is not a valid scheduling technique")

	if frontend_only:
		log.info("Early execution termination\n\nBye :)")




		###################### ASAP ######################
def asap(parser, base_path, example_name):
	scheduler = Scheduler(parser, "asap", log=log)
	scheduler.create_scheduling_ilp()
	status = scheduler.solve_scheduling_ilp(base_path, example_name)
	chart_title = "{0} - {1}".format("asap", example_name)
	scheduler.print_gantt_chart( chart_title, "{0}/{1}/{2}_{1}.pdf".format(base_path, example_name, "asap") )
	scheduler.print_scheduling_summary("{0}/{1}/{2}_{1}.txt".format(base_path, example_name, "asap") )


		###################### ALAP ######################
def alap(parser, base_path, example_name):
	asap = Scheduler(parser, "asap", log=log)
	asap.create_scheduling_ilp()
	status = asap.solve_scheduling_ilp(base_path, example_name)
	sink_svs = asap.get_sink_svs()

	scheduler = Scheduler(parser, "alap", log=log)
	scheduler.create_scheduling_ilp(sink_svs)
	status = scheduler.solve_scheduling_ilp(base_path, example_name)
	chart_title = "{0} - {1}".format("alap", example_name)
	scheduler.print_gantt_chart( chart_title, "{0}/{1}/{2}_{1}.pdf".format(base_path, example_name, "alap") )
	scheduler.print_scheduling_summary("{0}/{1}/{2}_{1}.txt".format(base_path, example_name, "alap") )

###################### ASAP with RESOURCE CONSTRAINTS sdc ######################

def asap_rconstrained(parser, base_path, example_name):
	scheduler = Scheduler(parser, "asap", log=log)
	scheduler.create_scheduling_ilp()

	ilp_dependency_inj = scheduler.pass_scheduling_ilp
	resource_manager = Resources(parser, ilp_dependency_inj, log=log)
	
	resouce_constraint_dict = {}
	resouce_constraint_dict["add"] = 1
	resouce_constraint_dict["mul"] = 1
	resouce_constraint_dict["zext"] = 1

	resource_manager.add_resource_constraints(resouce_constraint_dict)

	status = scheduler.solve_scheduling_ilp(base_path, example_name)

	chart_title = "{0} - {1}".format("asap resource constrained", example_name)
	scheduler.print_gantt_chart( chart_title, "{0}/{1}/{2}_{1}_resource_ADD_1_MUL_1.pdf".format(base_path, example_name, "asap"))
	scheduler.print_scheduling_summary("{0}/{1}/{2}_{1}_resource_ADD_1_MUL_1.txt".format(base_path, example_name, "asap") )


		###################### ASAP pipelined ######################

def pipelined(parser, base_path, example_name):
	status = 0
	ii = 0
	scheduler = 0
	while(status != 1):
		ii= ii + 1
		print(f"Trying II = {ii}")
		scheduler = Scheduler(parser, "pipelined", log=log)
		scheduler.create_scheduling_ilp(II=ii)
		status = scheduler.solve_scheduling_ilp(base_path, example_name)
	chart_title = "{0} - {1} (II: {2})".format("asap pipelined", example_name, ii)
	scheduler.print_gantt_chart( chart_title, "{0}/{1}/{2}_{1}_asap_pipelined.pdf".format(base_path, example_name, "pipelined"))
	scheduler.print_scheduling_summary("{0}/{1}/{2}_{1}_asap_pipelined.pdf.txt".format(base_path, example_name, "pipelined") )


		###################### ASAP pipelined resource constrained ######################

def pipelined_rconstrained(parser, base_path, example_name):
	chart_title = "{0} - {1}".format("asap pipelined resource constrained", example_name)
	status = 0
	ii = 0
	scheduler = 0
	succesful = False
	while not succesful:
		ii= ii + 1
		print(f"Trying II = {ii}")
		scheduler = Scheduler(parser, "pipelined", log=log)
		scheduler.create_scheduling_ilp(II=ii)
		
		resource_manager = Resource_Manager(parser, scheduler.pass_scheduling_ilp, log=log)
		resource_constraint_dict = {}
		resource_constraint_dict["mul"] = 1
		resource_constraint_dict["add"] = 1
		resource_constraint_dict["zext"] = 1
		resource_manager.add_resource_constraints(resource_constraint_dict)
		status = scheduler.solve_scheduling_ilp(base_path, example_name)

		succesful = resource_manager.check_resource_constraints_pipelined()

	scheduler.print_gantt_chart(chart_title, "{0}/{1}/{2}_{1}_asap_pipelined_res_constrained.pdf".format(base_path, example_name, "pipelined"))
	scheduler.print_scheduling_summary("{0}/{1}/{2}_{1}_asap_pipelined_res_constrained.txt".format(base_path, example_name, "pipelined") )

#todo: add desc in assignment
if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser(description="Welcome to the SDC project for the Summer Semester 2023!")
	arg_parser.add_argument('--input_list', type=str, help='Input filelist containing examples to run', default="filelist.lst")
	arg_parser.add_argument('--methods', type=str, help='Space-separated list of scheduling methods that should be run, all methods are tested when this is not specified.  Possible values are: asap, alap, asap_rconst, pipelined, pipelined_rconst, all')
	arg_parser.add_argument('--examples_folder', type=str, help='Path of the examples folder', default="examples")
	arg_parser.add_argument('--frontend', action='store_true' , help='Execute only frontend', default=False)
	arg_parser.add_argument('--debug', action='store_true' , help='Set debug mode', default=False)


	args = arg_parser.parse_args()

	main(args)
