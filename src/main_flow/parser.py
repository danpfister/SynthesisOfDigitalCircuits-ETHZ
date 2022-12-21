#!/usr/bin/python3
import os, argparse, re
import pygraphviz as pgv
import networkx as nx
from llvmlite.binding import parse_assembly

DEBUG = False

def get_gv_edges(gv):
	return map(lambda e : gv.get_edge(*e), gv.edges(keys=True))

def get_gv_nodes(gv):
	return map(lambda n : gv.get_node(n), gv.nodes())

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
				_parse_cdfg_instruction(str(instruction), self.cdfg, str(basic_block.name)) 
				#match_variable_declaration = re.search(r'%(\S+) = (.*)', str(instruction)) 
				#if match_variable_declaration != None: #check if the instruction is a variable declaration
				#	variable_name, variable_declaration = match_variable_declaration.group(1, 2)
				#	self.cdfg.add_node(f'{variable_name}', label = f'{str(instruction)}')
				#	if DEBUG:
				#		print("[DEBUG] Added node {0} for instruction {1}".format(variable_name, instruction))
				#	for operand in instruction.operands: #iterate through operands of instruction declaration
				#		operand_name = f'{operand}'.split("=")[0]
				#		operand_name = re.sub("\\s+","", operand_name)
				#		if len(operand_name) > 0:
				#			operand_variable_name = re.sub(r'%', '', operand_name)
				#			self.cdfg.add_edge(f'{operand_variable_name}', f'{variable_name}')
				#			if DEBUG:
				#				print("[DEBUG] Added edge {0} -> {1}".format(operand_variable_name, variable_name))
		for bb in set([ n.attr['bbID'] for n in get_gv_nodes(self.cdfg) if n.attr['bbID'] != '' ]):
			self.cdfg.add_subgraph([ str(n) for n in get_gv_nodes(self.cdfg) if n.attr['bbID'] == bb ], name = f'cluster_{bb}', color = 'darkgreen', label = bb)

	#function to draw cdfg function representation of the ssa input file
	def draw_cdfg(self, output_file = 'test.pdf', layout = 'dot'):
		assert(not(self.cdfg is None))
		self.cdfg.draw(output_file, prog=layout)
		self.cdfg.write(output_file.replace('.pdf', '.dot'))
		print("[Info] Printed cdfg in file {0} with layout {1}".format(output_file, layout))

# common regex
fast_math_flags = r'(nnan )?(ninf )?(nsz )?(arcp )?(contract )?(afn )?(reassoc )?(fast )?'
iarith_flags    = r'(nuw )?(nsw )?'

# regex for 2-input 1-output operators
binary_instructions = [
	('fneg', r'(\S+) = fneg ' + fast_math_flags + '(\S+) (\S+)'),        # <result> = fneg float %val          ; yields float:result = -%var
	('add',  r'(\S+) = add '  + iarith_flags + '(\S+) (\S+), (\S+)'),    # <result> = add nuw nsw <ty> <op1>, <op2>  ; yields ty:result
	('fadd', r'(\S+) = fadd ' + fast_math_flags + '(\S+) (\S+), (\S+)'), 
	('sub',  r'(\S+) = sub '  + iarith_flags + '(\S+) (\S+), (\S+)'),    
	('mul',  r'(\S+) = mul '  + iarith_flags + '(\S+) (\S+), (\S+)'),    
	('fmul', r'(\S+) = fmul ' + fast_math_flags + '(\S+) (\S+), (\S+)'), 
	('udiv', r'(\S+) = udiv ' + r'(exact )?' + '(\S+) (\S+), (\S+)'), 
	('sdiv', r'(\S+) = sdiv ' + r'(exact )?' + '(\S+) (\S+), (\S+)'), 
	('fdiv', r'(\S+) = fdiv ' + fast_math_flags + '(\S+) (\S+), (\S+)'), 
	('urem', r'(\S+) = urem (\S+) (\S+), (\S+)'), 
	('srem', r'(\S+) = srem (\S+) (\S+), (\S+)'), 
	('frem', r'(\S+) = frem ' + fast_math_flags + '(\S+) (\S+), (\S+)'), 
	('lshr',  r'(\S+) = lshr ' + r'(exact )?' + '(\S+) (\S+), (\S+)'),    
	('ashr',  r'(\S+) = ashr ' + r'(exact )?' + '(\S+) (\S+), (\S+)'),    
	('and',   r'(\S+) = and (\S+) (\S+), (\S+)'), 
	('or',   r'(\S+) = or (\S+) (\S+), (\S+)'), 
	('xor',   r'(\S+) = xor (\S+) (\S+), (\S+)'), 
	('icmp', r'(\S+) = icmp (\S+) (\S+) (\S+), (\S+)')                   # <result> = icmp <cond> <ty> <op1>, <op2>   ; yields i1 or <N x i1>:result
]
unary_instructions = [
	('fneg', r'(\S+) = fneg ' + fast_math_flags + '(\S+) (\S+)'),        # <result> = fneg float %val          ; yields float:result = -%var
	('zext', r'(\S+) = zext (\S+) (\S+) to (\S+)'),
	('sext', r'(\S+) = sext (\S+) (\S+) to (\S+)')
]
memory_instructions = [
	('load',  r'(\S+) = load (volatile )?(\S+), (\S+) ([\w%]+),?\s?(align \S+)?,?\s?'),
	('store', r'store (volatile )?(\S+) (\S+), (\S+) ([\w%]+),?\s?(align \S+)?,?\s?'),
	('getelementptr', r'(\S+) = getelementptr inbounds (\S+), (\S+) (\S+), (\S+) (\S+)') #<result> = getelementptr inbounds <ty>, ptr <ptrval>{, [inrange] <ty> <idx>}*
]
control_instructions = [
	('ret',  r'ret (\S+)? (\S+)'),                                       # ret <type> <value> ; Return a value from a non-void function
	('br',   r'br i1 (\S+), label (\S+), label (\S+)'),                  # br i1 <cond>, label <iftrue>, label <iffalse>
	('jmp',   r'label (\S+)'),                                            # br label <dest>          ; Unconditional branch
	('phi', r'(\S+) = phi ' + fast_math_flags + '(\S+) (\[ \S+, \S+ \]),?\s?(\[ \S+, \S+ \])?')
]

# parse individual instruction
def _parse_cdfg_instruction(inst, cdfg, bbID):
	assert type(inst) == str
	operands, result, label = [], '', inst
	for type_, regex in binary_instructions:
		match = re.search(regex, inst)
		if match:
			operands = [ n for n in match.groups() if n != None][-2:]
			result = match.group(1)
			if type_ == 'icmp': label = 'icmp ' + match.group(2) + ' ' + result
			else: label = type_ + ' ' + result
	for type_, regex in unary_instructions:
		match = re.search(regex, inst)
		if match and 'ext' in type_:
			operands = [match.group(3)]
			result = match.group(1)
			label = type_
		elif match and type_ == 'fneg':
			operands = [ n for n in match.groups() if n != None][-1]
			result = match.group(1)
			label = type_
	for type_, regex in memory_instructions:
		match = re.search(regex, inst)
		if match and type_ == 'load':
			operands = [ match.group(5) ]
			result = match.group(1)
			label = 'load ' + result
		elif match and type_ == 'store':
			operands = match.group(3, 5)
			result = 'store ' + match.group(5)
			label = 'store ' + result
		elif match and type_ == 'getelementptr':
			operands = match.group(4, 6)
			result = match.group(1)
			label = type_ + ' ' + result
	for type_, regex in control_instructions:
		match = re.search(regex, inst)
		if match and type_ == 'ret':
			operands = [match.group(2)]
			result = f'ret {bbID}'
			label = result
		if match and type_ == 'br':
			operands = [match.group(1)]
			result = f'br {bbID}'
			label = result
		if match and type_ == 'phi':
			result = match.group(1)
			label = type_ + ' ' + result
			predecessors = [ n for n in match.groups() if n != None][-2:]
			#for p in predecessors:
			#	value, bbID = re.match(r'\[ (\S+), (\S+) \]', p).group(1, 2)
			#	value = 'br ' + value.replace('%', '')
			#	bbID = bbID.replace('%', '')
			#	print(value)
			#	print(bbID)
			#	print(result)
			#	cdfg.add_node(f'br {bbID}')
			#	cdfg.add_node(f'{result.replace("%", "")}')
			#	cdfg.add_edge(f'br {bbID}', f'{result.replace("%", "")}')
			
	result = result.replace('%', '')
	constants = [ op for op in operands if '%' not in op ]
	operands = [ op.replace('%', '') for op in operands if '%' in op ]
	if result != '':
		#cdfg.add_node(f'{result}', label = f'{inst.strip()}', bbID = bbID)
		cdfg.add_node(f'{result}', label = label, bbID = bbID, inst = inst.strip())
		for input_ in operands:
			cdfg.add_node(f'{input_}')
			cdfg.add_edge(f'{input_}', f'{result}')
		for input_ in constants:
			cdfg.add_node(f'{input_}', bbID = bbID)
			cdfg.add_edge(f'{input_}', f'{result}')


if __name__ == '__main__':
	args_parser = argparse.ArgumentParser(description="SSA parser")

	args_parser.add_argument('--ssa_path', type=str, help='SSA input file path', default = None)
	args = args_parser.parse_args()
	
	if args.ssa_path == None:
		print("[ERROR] You have to specify the ssa file path")
		exit(-1)

	ssa_parser = Parser(args.ssa_path)
