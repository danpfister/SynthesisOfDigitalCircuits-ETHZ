import re, json
import pygraphviz as pgv
from llvmlite.binding import parse_assembly

if __name__ == '__main__':
	print("[ERROR] Use option --frontend with the run_SDC.py script to run only the parser")
	exit()

# this imports are relative to SDC main path, so they shouldn't be run if the script run on its own
from src.utilities.regex import *
from src.utilities.cdfg_manager import *


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
				# finding and setting inputs of function
				for line in str(function).split("\n"):
					if "define" in line and top_function_name in line:
						input_regex = r'\(((, )?(\S+)\* %(\S+))*\)'
						match_input = re.search(input_regex, line)
						matched_string = match_input.group()
						splitted_matched_string = matched_string.split()
						self.function_inputs = []
						for i in range(len(splitted_matched_string)):
							if i % 2 != 0:
								self.function_inputs.append(splitted_matched_string[i].replace(",","").replace(")","").replace("%","_"))

	#function to create the cdfg representation of the assembly code
	def create_cdfg(self):
		assert(not(self.top_function is None)) #check that top_function it not None and the set_top_function has been called at least once
		self.cdfg = pgv.AGraph(strict=False, directed=True)
		for basic_block in self.top_function.blocks: #iterate trough basic blocks to generate the cdfg with instructions as nodes
			for instruction in basic_block.instructions:
				self.parse_cdfg_instruction(str(instruction), self.cdfg, str(basic_block.name)) # each instruction is instantiated inside the cdfg
		for bb_id in set([ bb_node.attr['bbID'] for bb_node in get_cdfg_nodes(self.cdfg) if bb_node.attr['bbID'] != '' ]): # iterating through the BB ids to recreate BB graph
			self.cdfg.add_subgraph([ str(cdfg_node) for cdfg_node in get_cdfg_nodes(self.cdfg) if cdfg_node.attr['bbID'] == bb_id ], name = f'cluster_{bb_id}', color = 'darkgreen', label = bb_id)
																															# associating to each node in the cdfg the corresponding BB id it belongs to

	# functio to parse each instruction
	def parse_cdfg_instruction(self, instruction, cdfg, bbID):
		assert type(instruction) == str # the instruction input type should be string
		operands, result, label = [], '', instruction
		# iterating through all regex instruction to indentify a candidate instruction
		for instruction_key, instruction_regex in all_regex_instructions.items():
			match = re.search(instruction_regex, instruction)
			if match:
				# depending on the type of instruction different information extraction are applied
				# the match groups depend on the regex (see utilities.regex.py for detailed list of regex)
				# binary intruction case
				if instruction_key in binary_instructions: # instruction format: result = binary_instruction output_type input_1 input_2
					operands = [ n for n in match.groups() if n != None][-2:]
					result = match.group(1)
					if instruction_key == 'icmp': label = 'icmp ' + match.group(2) + ' ' + result # icmp instruction format: result = icmp icmp_type output_type input_1 input_2
					else: label = instruction_key + ' ' + result
				# unary instruction case 
				elif instruction_key in unary_instructions:
					if "ext" in instruction_key: # instruction format: result = unary_instruction input_type input to output_type
						operands = [match.group(3)]
						result = match.group(1)
						label = instruction_key + ' ' + result
					elif instruction_key == "fneg": # fneg instruction format: result = fneg output_type input 
						operands = [ n for n in match.groups() if n != None][-1]
						result = match.group(1)
						label = instruction_key + ' ' + result
				# memory instruction case
				elif instruction_key in memory_instructions:
					if "load" in instruction_key:
						operands = [ match.group(5) ]
						result = match.group(1)
						label = 'load ' + result
					elif instruction_key == 'store':
						operands = match.group(3, 5)
						result = 'store ' + match.group(5)
						label = 'store ' + result
					elif instruction_key == 'getelementptr':
						operands = match.group(4, 6)
						result = match.group(1)
						label = instruction_key + ' ' + result
				# control instruction case
				elif instruction_key in control_instructions:
					if instruction_key == 'ret':
						operands = [match.group(2)]
						result = f'ret {bbID}'
						label = result
					elif instruction_key == 'br':
						operands = [match.group(1)]
						result = f'br {bbID}'
						label = result
					elif instruction_key == 'phi':
						result = match.group(1)
						label = instruction_key + ' ' + result
						input_regex = r'\[(\s)*(\S+)(\s)*,(\s)*(\S+)(\s)*\]' # input format: [value, label]
						for n in match.groups()[-2:]:
							if n != None:
								match_input = re.search(input_regex,n)
								if match_input != None:
									operands.append(match_input.group(2))
				else:
					print("[ERROR] Identifying instruction '{0}'".format(instruction))

				break
				
		result = result.replace('%', '_')
		constants = [ op for op in operands if '%' not in op ] # constants are operands without initial '%' symbol
		variables = [ op.replace('%', '_') for op in operands if '%' in op ] # variables are operands with initial '%' symbol
		if result != '':
			cdfg.add_node(f'{result}', label = label.replace('%', '_'), bbID = bbID, instruction = instruction.strip()) # add node related to the instruction
			if DEBUG:
				print("[DEBUG] Added node {0} with input variable {1} and input constant {2}".format(label, variables, constants))
			for input_ in variables: # add a node for each input variable if not present and the edge connecting it to result
				if input_ in self.function_inputs: # if the variable is a function input, the bbid is assigned depending on last operation calling it
					cdfg.add_node(f'{input_}', bbID = bbID)					
				else:
					cdfg.add_node(f'{input_}')
				cdfg.add_edge(f'{input_}', f'{result}')
				if DEBUG:
					print("[DEBUG] Added variable node {0} and edge {0} -> {1}".format(input_, result))
			for input_ in constants: # add a node for each input constant and the edge connecting it to result
				cdfg.add_node(f'{input_}', bbID = bbID)
				cdfg.add_edge(f'{input_}', f'{result}')
				if DEBUG:
					print("[DEBUG] Added constant node {0} and edge {0} -> {1}".format(input_, result))

	#function to draw cdfg function representation of the ssa input file
	def draw_cdfg(self, output_file = 'test.pdf', layout = 'dot'):
		assert(not(self.cdfg is None))
		self.cdfg.draw(output_file, prog=layout)
		self.cdfg.write(output_file.replace('.pdf', '.dot'))
		print("[Info] Printed cdfg in file {0} with layout {1}".format(output_file, layout))

