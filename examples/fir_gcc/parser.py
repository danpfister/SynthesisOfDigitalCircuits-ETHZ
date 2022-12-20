#!/usr/bin/python3
import os, re, argparse, pprint
import pygraphviz as pgv
import networkx as nx
from itertools import combinations, product
from glob import glob



def main(args):
	fname, fbody = _extract_kernel(args)
	fbody = re.findall(r'\{(.*)\}', fbody, flags=re.MULTILINE | re.DOTALL)[0]
	# split the kernel according to BB tags
	print("----------------------")
	blocks = re.split(r'<bb \d+>\s*:', fbody, flags=re.MULTILINE)
	print(len(blocks))
	for bb in blocks:
		print(bb)


def _extract_kernel(args):
	with open(args.ssa, 'r') as f:
		ftext = f.read()
	functions = re.findall(r';; Function (\w+) \(', ftext)
	fbodies = re.split(r'^;; Function \w+ .*$', ftext, flags=re.MULTILINE)
	return functions[0], fbodies[1]



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="dot2smv")
	# default top-level file
	try:
		proj_name = os.path.basename(glob("./src/*.cpp")[0]).replace(".cpp", "")
	except IndexError:
		proj_name = ''
	
	parser.add_argument('--ssa', type=str, help='input .ssa file', default=f"./reports/{proj_name}.cpp.023t.ssa")
	parser.add_argument('--dfg', type=str, help='input .cfg file', default=f"./reports/{proj_name}.cpp.023t.cfg")
	args = parser.parse_args()
	main(args)
