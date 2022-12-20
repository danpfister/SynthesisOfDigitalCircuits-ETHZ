#!/bin/bash
{

# top-level file (remember to change these variables accordingly)
PROJ_DIR="."
PROJ_NAME=$(basename $(ls ${PROJ_DIR}/src/*.cpp| head -1) | sed 's/.cpp//g')
TOP_FILE="${PROJ_NAME}.cpp"
mkdir reports 2> /dev/null

# generate SSA
gcc -fno-inline -fdump-tree-ssa -fdump-tree-cfg -dumpdir ./reports/ -S -O3 ./src/$TOP_FILE

} 2>&1 | tee output.log
