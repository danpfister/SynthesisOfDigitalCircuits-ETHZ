#!/bin/bash 
export LLVM_BIN=/local/home/crizzi/dynamatic_install_folder/etc/llvm-6.0/bin
export CLANG=$LLVM_BIN/clang
export OPT=$LLVM_BIN/opt

## top-level file (remember to change these variables accordingly)
PROJ_DIR="."
PROJ_NAME=$(basename $(ls ${PROJ_DIR}/src/*.cpp| head -1) | sed 's/.cpp//g')
TOP_FILE="${PROJ_NAME}.cpp"

name=${PROJ_NAME}.cpp
SRC_DIR=src
REPORT_DIR=reports 

OPTIMIZATON_LEVEL= #O1, O2, O3
OPTIMIZATION_FLAGS= #-fno-builtin, -fno-vectorize

rm -r ./reports 2> /dev/null

mkdir ./reports 

{

$CLANG -Xclang -disable-O0-optnone -emit-llvm -S $OPTIMIZATION_LEVEL $OPTIMIZATION_FLAGS -c $SRC_DIR/$name -o $name.ll
$OPT -mem2reg $name.ll -S -o $name"_mem2reg.ll"
$OPT -loop-rotate -constprop  $name"_mem2reg.ll" -S -o $name"_mem2reg_constprop.ll"
$OPT -simplifycfg $name"_mem2reg_constprop.ll" -S -o $name"_mem2reg_constprop_simplifycfg.ll"
$OPT -die -instcombine -lowerswitch $name"_mem2reg_constprop_simplifycfg.ll" -S -o $name"_mem2reg_constprop_simplifycfg_die.ll" 

mv *.ll ./reports

} 2>&1 | tee output.log
