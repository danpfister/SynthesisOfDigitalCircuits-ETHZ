# Course Project: Implement Your Modulo Scheduler (SDC-SDC)

## Introduction

This is the repository for the first student project in the course **Synthesis of Digital Circuits**.
The goal of this project is to practice the theory of modulo scheduling we have covered in this lecture.

Starting from an optimized intermediate representation (IR), we would like to investigate into the following steps:

1. Deriving a set of data/control dependencies that the schedule should respect;
2. Deriving a set of loop-carried dependencies that a pipelined schedule should respect;
3. From the set of depedencies, deriving a set of MILP constraints on the scheduling variables (SV), and the initialization intervals (II).
4. Run the MILP solver to get the optimal values of SVs and IIs.
5. Extract the corresponding schedule from the SVs and IIs.

## Package Dependencies

### Graphviz (A Graph Visualization Engine)

On Ubuntu machines, you can get the required dependencies via package manager:

```sh
sudo apt-get install graphviz graphviz-dev
``` 

### Cbc (A MILP Solver)

On Ubuntu machines, you can get the required dependencies via package manager:

```sh
sudo apt-get install cbc
``` 

### Python
```
python 3.7
pygraphviz 1.9
llvmlite 0.39.1
PuLP 2.7.0
networkx 2.8
``` 
### LLVM (Compiler Frontend, Optional)

As in many HLS compilers, we use LLVM as the frontend to generate intermediate representation (IR) from C code.
For the purpose of this project, we provide the IR code of the HLS kernels of the assignments.

## An Overview of the Main Flow

The main flow consists of the following parts. The relevent source code can be found in `./src/main_flow` directory.

- `llvm_ir.sh`: A script that compiles C/C++ code down to optimized LLVM IR (optional).
- `parser.py`: A library that converts LLVM IR to Control and Dataflow Graph (CDFG).
- `sdc.py`: A library that produces a set of constraints for modulo scheduling (**Your turn to complete**).
- `schedule.py`: A script that converts the scheduling variable and II into a valid schedule.

Besides the main scheduling flow, we also provide a set of utility libraries.
You can find these utilities in `./src/utilities` directory.
Please do not modify them, as stick to these utilities as much as possible when developing your own `sdc.py`.

- `cdfg_manager.py`: a library of utility functions for manipulating the CDFG (e.g., adding or deleting nodes and edges, modifying attributes).
- `ilp_manager.py`: a library that provides you an API to interact with the MILP solver.
- `regex.py`: the regexes used across this project.  
