#!/bin/python3
import argparse
from src.main_flow.parser import Parser
from src.main_flow.scheduler import Scheduler
from src.main_flow.resource import Resources
import logging

# create log interface
log = logging.getLogger('sdc')
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler() # create console handler and set level to debug
formatter = logging.Formatter('%(levelname)s - %(message)s') # create formatter
console_handler.setFormatter(formatter) # add formatter to console
log.addHandler(console_handler) # add console_handler to log


def main(args):
	frontend_only = args.frontend
	input_list = args.input_list
	base_path = args.examples_folder
	debug_mode = args.debug

	log.info("Arguments selected:\n\tINPUT LIST = {0}\n\tEXAMPLE FOLDER PATH = {1}\n\tONLY FRONTEND = {2}\n\tDEBUG = {3}".format(frontend_only, base_path, input_list, debug_mode))

	# if debug_mode is selected logger is set to debug
	if debug_mode:
		log.setLevel(logging.DEBUG)

	#reading the list of examples to execute
	examples_list_file = open(input_list, "r")
	examples_list = examples_list_file.read().split("\n")
	examples_list_file.close()

	for example_name in examples_list:
		if example_name == "":
			continue

		log.info("*** BENCHMARK {0} ***".format(example_name))
		# the path of the ssa file should be base_path/example_name/reports/example_name.cpp_mem2reg_constprop_simplifycfg_die.ll
		path_ssa_example = "{0}/{1}/reports/{1}.cpp_mem2reg_constprop_simplifycfg_die.ll".format(base_path, example_name)

		log.info("Parsing file {0}".format(path_ssa_example))
		ssa_parser = Parser(path_ssa_example, example_name, log)
		if not(ssa_parser.is_valid()):
			log.error("Parser has encountered a problem. Please verify path correctness ({0})".format(path_ssa_example))
			continue
		ssa_parser.draw_cdfg("{0}/{1}/test.pdf".format(base_path, example_name))

		scheduling_type = "asap"
		scheduler = Scheduler(ssa_parser, scheduling_type, log=log)
		scheduler.create_scheduling_ilp()
		ilp, constraints, opt_function = scheduler.get_ilp_tuple()
		scheduler.solve_scheduling_ilp(base_path, example_name)
		sink_delays = scheduler.get_sink_delays()


		scheduling_type = "alap"
		scheduler = Scheduler(ssa_parser, scheduling_type, log=log)
		scheduler.create_scheduling_ilp(sink_delays)
		ilp, constraints, opt_function = scheduler.get_ilp_tuple()
		resource_manager = Resources(ssa_parser, { 'load' : 2, 'add' : 1 }, log=log)
		resource_manager.add_resource_constraints(ilp, constraints, opt_function)
		scheduler.solve_scheduling_ilp(base_path, example_name)
		chart_title = "{0} - {1}".format(scheduling_type, example_name)
		scheduler.print_gantt_chart( chart_title, "{0}/{1}/{2}_{1}.pdf".format(base_path, example_name, scheduling_type) )

	if frontend_only:
		log.info("Early execution termination\n\nBye :)")


if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser(description="Welcome to the SDC project for the Summer Semester 2023!")
	arg_parser.add_argument('--input_list', type=str, help='Input filelist containing examples to run', default="filelist.lst")
	arg_parser.add_argument('--examples_folder', type=str, help='Path of the examples folder', default="examples")
	arg_parser.add_argument('--frontend', action='store_true' , help='Execute only frontend', default=False)
	arg_parser.add_argument('--debug', action='store_true' , help='Set debug mode', default=False)


	args = arg_parser.parse_args()

	main(args)
