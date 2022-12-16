#!/bin/bash
{

# top-level file (remember to change these variables accordingly)
PROJ_DIR="."
PROJ_NAME=$(basename $(ls ${PROJ_DIR}/src/*.cpp| head -1) | sed 's/.cpp//g')
TOP_FILE="${PROJ_NAME}.cpp"
rm $PROJ_NAME* 2> /dev/null

# generate SSA
gcc -fdump-tree-ssa -S -O0 ./src/$TOP_FILE

# generate CFG
gcc -fdump-tree-cfg -S -O0 ./src/$TOP_FILE

} 2>&1 | tee output.log
