#!/usr/bin/python3
import os, re, argparse, pprint
import pygraphviz as pgv
import networkx as nx
from itertools import combinations, product
from glob import glob

def draw_gv(gv, name = 'test.pdf', prog = 'dot'):
	gv.draw(name, prog="dot")


def main(args, proj_name):
	from llvmlite.binding import parse_assembly, get_function_cfg
	with open(args.ssa, 'r') as f:
		ssa = f.read()
	print("AAAAAAAAAAAAA", args.ssa)
	instance = parse_assembly(ssa)
	instance.verify()
	#print(instance)
	for func in instance.functions:
		if re.search(proj_name, func.name):
			top_function = func
	#print(top_function.name)
	#print(top_function)
	#print('------------------------------------')
	cdfg = pgv.AGraph(strict=False, directed=True)
	instructions = []
	for bb in top_function.blocks:
		#print('==============================')
		#print(bb.name)
		#print('------------------------------------')
		#for id_, inst in enumerate(bb.instructions):
		#	print(f'Instruction {id_}: {inst}')
		#	if inst.name != '':
		#		print(f'Opcode: {inst.opcode}')
		#		print(f'Name of the result: %{inst.name}')
		#		print(f'Operands: {[", ".join([n.name for n in inst.operands])]}')
		for inst in bb.instructions:
			instructions.append(inst)
		#	print(f'Type: {inst.type}')
	for inst in instructions:
		match = re.search(r'%(\S+) = (.*)', str(inst))
		if match:
			name, rest = match.group(1, 2)
			cdfg.add_node(f'{name}', label = f'{str(inst)}')
	for inst in instructions:
		match = re.search(r'%(\S+) = (.*)', str(inst))
		if match:
			name, rest = match.group(1, 2)
			for pred in inst.operands:
				pn = re.sub(r'%', '', pred.name)
				#print(pred.name)
				#print(len(pred.name))
				if pred.name != '':
					#print((f'{pn}', f'{name}'))
					cdfg.add_edge(f'{pn}', f'{name}')
	#print(cdfg.nodes)
	#print(cdfg.edges)
	draw_gv(cdfg)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="dot2smv")
	# default top-level file
	try:
		proj_name = os.path.basename(glob("./src/*.cpp")[0]).replace(".cpp", "")
	except IndexError:
		proj_name = ''
	
	parser.add_argument('--ssa', type=str, help='input .ll file', default=f"./reports/{proj_name}.cpp_mem2reg_constprop_simplifycfg_die.ll")
	args = parser.parse_args()
	main(args, proj_name)
