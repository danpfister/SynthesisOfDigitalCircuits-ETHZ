#!/bin/python3
import argparse
from src.main_flow.parser import Parser
from src.main_flow.scheduler import Scheduler
import logging

log = logging.getLogger('sdc')
log.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to log
log.addHandler(ch)

def main(args):
	frontend_only = args.frontend
	input_list = args.input_list
	base_path = args.examples_folder

	log.info("Arguments selected:\n\tINPUT LIST = {0}\n\tEXAMPLE FOLDER PATH = {1}\n\tONLY FRONTEND = {2}".format(frontend_only, base_path, input_list))
	print("[INFO] Arguments selected:\n\tINPUT LIST = {0}\n\tEXAMPLE FOLDER PATH = {1}\n\tONLY FRONTEND = {2}".format(frontend_only, base_path, input_list))

	#reading the list of examples to execute
	examples_list_file = open(input_list, "r")
	examples_list = examples_list_file.read().split("\n")
	examples_list_file.close()

	for example_name in examples_list:
		if example_name == "":
			continue
		# the path of the ssa file should be base_path/example_name/reports/example_name.cpp_mem2reg_constprop_simplifycfg_die.ll
		path_ssa_example = "{0}/{1}/reports/{1}.cpp_mem2reg_constprop_simplifycfg_die.ll".format(base_path, example_name)

		log.info("Parsing file {0}".format(path_ssa_example)) 
		print("[Info] Parsing file {0}".format(path_ssa_example))
		ssa_parser = Parser(path_ssa_example, example_name)
		if not(ssa_parser.is_valid()):
			log.error("Parser has encountered a problem. Please verify path correctness ({0})".format(path_ssa_example))
			print("[ERROR] Parser has encountered a problem. Please verify path correctness ({0})".format(path_ssa_example))
			continue
		ssa_parser.draw_cdfg("{0}/{1}/test.pdf".format(base_path, example_name))

		scheduler = Scheduler(ssa_parser, "pipelined")
		scheduler.set_data_dependency_constraints()
		scheduler.set_resource_constraints()
		scheduler.set_II_constraints()
		scheduler.set_opt_function()
		scheduler.find_optimal_schedule(base_path, example_name)

	if frontend_only:
		print("[Info] Early execution termination\n\nBye :)")


if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser(description="Welcome to the SDC project for the Summer Semester 2023!")
	arg_parser.add_argument('--input_list', type=str, help='Input filelist containing examples to run', default="filelist.lst")
	arg_parser.add_argument('--examples_folder', type=str, help='Path of the examples folder', default="examples")
	arg_parser.add_argument('--frontend', action='store_true' , help='Execute only frontend', default=False)


	args = arg_parser.parse_args()

	main(args)
