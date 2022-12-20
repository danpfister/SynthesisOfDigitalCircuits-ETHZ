#!/usr/bin/python3
import os, argparse, re
import pygraphviz as pgv
import networkx as nx
from llvmlite.binding import parse_assembly

DEBUG = False

class Parser():

	def __init__(self, ssa_path, example_name):
		self.ssa_path = ssa_path
		self.example_name = example_name

		self.read_ssa_file(ssa_path) #function to set the parser assembly
		self.set_top_function(example_name) #it assumes that the filename corresponds to top function
		self.create_cdfg()

	#function to check validity of the parser
	def is_valid(self):
		valid = True
		if self.ssa_path == None or not(".ll" in self.ssa_path):
			print("[ERROR] SSA path is wrong ({0}). Please check the correct path and the correct format (.ll)".format(self.ssa_path))
			valid = False
		if self.assembly == None:
			print("[ERROR] Assembly is invalid. You need to call read_ssa_file function at least once")
			valid = False
		if self.top_function == None:
			print("[ERROR] Top_function is invalid. You need to call set_top_function function at least once")
			valid = False
		return valid

	#function to read ssa file and check its validity
	def read_ssa_file(self, ssa_path):

		with open(ssa_path, 'r') as f:
			ssa = f.read()
		self.assembly = parse_assembly(ssa)
		self.assembly.verify()
	
	#function to set top function of the input assembly file
	def set_top_function(self, top_function_name):
		assert(not(self.assembly is None)) #check that assembly is not None and the read_ssa_file has been called at least once
		for function in self.assembly.functions:
			if re.search(top_function_name, function.name):
				self.top_function = function

	#function to create the cdfg representation of the assembly code
	def create_cdfg(self):
		assert(not(self.top_function is None)) #check that top_function it not None and the set_top_function has been called at least once
		self.cdfg = pgv.AGraph(strict=False, directed=True)
		for basic_block in self.top_function.blocks: #iterate trough basic blocks to generate the cdfg with instructions as nodes
			for instruction in basic_block.instructions:
				match_variable_declaration = re.search(r'%(\S+) = (.*)', str(instruction)) 
				if match_variable_declaration != None: #check if the instruction is a variable declaration
					variable_name, variable_declaration = match_variable_declaration.group(1, 2)
					self.cdfg.add_node(f'{variable_name}', label = f'{str(instruction)}')
					if DEBUG:
						print("[DEBUG] Added node {0} for instruction {1}".format(variable_name, instruction))
					for operand in instruction.operands: #iterate through operands of instruction declaration
						operand_name = f'{operand}'.split("=")[0]
						operand_name = re.sub("\\s+","", operand_name)
						if len(operand_name) > 0:
							operand_variable_name = re.sub(r'%', '', operand_name)
							self.cdfg.add_edge(f'{operand_variable_name}', f'{variable_name}')
							if DEBUG:
								print("[DEBUG] Added edge {0} -> {1}".format(operand_variable_name, variable_name))


	#function to draw cdfg function representation of the ssa input file
	def draw_cdfg(self, output_file = 'test.pdf', layout = 'dot'):
		assert(not(self.cdfg is None))
		self.cdfg.draw(output_file, prog=layout)
		print("[Info] Printed cdfg in file {0} with layout {1}".format(output_file, layout))


if __name__ == '__main__':
	args_parser = argparse.ArgumentParser(description="SSA parser")

	args_parser.add_argument('--ssa_path', type=str, help='SSA input file path', default = None)
	args = args_parser.parse_args()
	
	if args.ssa_path == None:
		print("[ERROR] You have to specify the ssa file path")
		exit(-1)

	ssa_parser = Parser(args.ssa_path)
