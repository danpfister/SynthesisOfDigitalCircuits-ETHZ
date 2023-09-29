#!/usr/bin/env python3
import os, sys

# make sure that the obfuscated script loads current dir
sys.path.insert(0, './')
import inspect
import re
import logging
import argparse
from collections import defaultdict
from src.main_flow.parser import Parser
from src.main_flow.scheduler import Scheduler
from src.main_flow.resource import Resource_Manager
from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
from typing import Dict, Any
import hashlib
import json
def dict_hash(dictionary: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    print(encoded)
    dhash.update(encoded)
    return dhash.hexdigest()

run_secret_tests = False #set this to false when building the obfuscated binary for the students
supersekrittest = [["fir",1], ["test_initiation_interval_1",1], ["test_initiation_interval_2",1], ["test_initiation_interval_3",1], ["test_memory_2",1], ["test_control_dependency_2",0],   ["test_data_dependency_1",0],  ["test_resources_constraints_1",0], ["test_control_dependency_1",0], ["test_data_dependency_2",0],   ["test_resources_constraints_2",0]]


refhashes = defaultdict(dict)
refhashes["kernel_1"]["asap"]                = "ab354be06f45c943ae3c8c5ec3d62778"
refhashes["kernel_1"]["alap"]                = "c6bc886a0777c22e6871d3fded0d667d"
refhashes["kernel_1"]["asap_rconst"]         = "ab354be06f45c943ae3c8c5ec3d62778"
refhashes["kernel_1"]["pipelined"]           = "5205c2467e1d091e047eed8236f163d0"
refhashes["kernel_1"]["pipelined"]           = "5205c2467e1d091e047eed8236f163d0"
refhashes["kernel_2"]["asap"]                = "c74a3ec9b2312b729e7eb040b8bd40a2"
refhashes["kernel_2"]["alap"]                = "8c566de950f6124f1b1b63d3956b3608"
refhashes["kernel_2"]["asap_rconst"]         = "c74a3ec9b2312b729e7eb040b8bd40a2"
refhashes["kernel_2"]["pipelined"]           = "187c7b04bb7e564cc9f7bae96bef0e9e"
refhashes["kernel_2"]["pipelined_rconst"]    = "187c7b04bb7e564cc9f7bae96bef0e9e"
refhashes["kernel_3"]["asap"]                = "67e6577f9052fe223e343e997e643886"
refhashes["kernel_3"]["alap"]                = "b2510c6ade778b5bb474ed1f49df7272"
refhashes["kernel_3"]["asap_rconst"]         = "4d5c46799a7a1159228f5e303e5579d1"
refhashes["kernel_3"]["pipelined"]           = "90d188434ee1205f3f6132e3e318bc91"
refhashes["kernel_3"]["pipelined_rconst"]    = "84ded022aff2a8237b4f52099097b7d1"
refhashes["kernel_4"]["asap"]                = "b24952a77fb63d848ea955361ca46906"
refhashes["kernel_4"]["alap"]                = "59cabc5a5865ef60384cc52d22db3fed"
refhashes["kernel_4"]["asap_rconst"]         = "c6e3d979b5939c89e08a2149258e8c45"
refhashes["kernel_4"]["pipelined"]           = "6f1f800407a2a7ad287b9ae808d5933e"
refhashes["kernel_4"]["pipelined_rconst"]    = "f2dc0c0dd54136d65385f07d984a4e5b"



#28 4:43
#color codes
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
class testfailed(Exception):
    pass


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, currentdir)

log = logging.getLogger('sdc')
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler() # create console handler and set level to debug
formatter = logging.Formatter('%(levelname)s - %(message)s') # create formatter
console_handler.setFormatter(formatter) # add formatter to console
log.addHandler(console_handler) # add console_handler to log

#scheduler, the scheduler object being tested,
#args given to the tester, optional
def example_test(scheduler,args):
    '''
    if the test passes it should return this: return bcolors.OKGREEN + "Passed" + bcolors.ENDC
    if if fails it should return: return bcolors.FAIL + "Failed" + bcolors.ENDC
    
    the test itself should only return bcolors.FAIL + "Crash " + bcolors.ENDC if there was a try block in the test itself which caught an exception
    the test should always be called from within a try statement and if it causes an exception the variable storing the result should be set to bcolors.FAIL + "Crash " + bcolors.ENDC
    if it doesnt cause an exception the variable should be set to the return value of the test
    '''
    pass

def main(args):
    # scheduling_type = args.technique
    print(f" name check {args.no_name_check} verbose: {args.verbose} supernode connection test: {args.no_snode_conn}")
    if args.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.ERROR)

    #parse given kernel list
    if args.kernels != None:
        ksplit = args.kernels.split()
        kernels = [n.split(",") for n in ksplit]
        print(kernels)
        #check numbers and if valid convert from string to int
        for k in kernels:
            if int(k[1]) != 0 and int(k[1]) !=1:
                error(f"Wrong pipeline enable value {k[1]} specified")
                return False
            else:
                k[1] = int(k[1])
    else:
        #name and whether pipelined schedulers should be tested
        kernels = [["kernel_1", 0], ["kernel_2", 0] , ["kernel_3", 1], ["kernel_4", 1]]
        #only append these if user doesn't explicitly requests some kernels
        if run_secret_tests == True:
            kernels.extend(supersekrittest)
            print(kernels)
    print("oy")
    print(log.getEffectiveLevel())

    #check the specified scheduling method(s)
    allowed_techniques = ["asap", "alap", "asap_rconst", "pipelined", "pipelined_rconst"]
    if args.methods != None:
        techniques = args.methods.split()
        for t in techniques:
            if t not in allowed_techniques:
                error(f"{t} is not a valid scheduling method")
                error(f"allowed methods are {allowed_techniques}")
                return False
    else:
        techniques = allowed_techniques
        
    results = defaultdict(dict)
    #save hashes of the ilp solution here for checking against master solution's results
    hashes = defaultdict(dict)
    base_path = "examples"

    for example_name in kernels:
        results[example_name[0]] = defaultdict(dict)
        hashes[example_name[0]] = defaultdict(dict)
        
        if example_name[0] == "":
                continue
            
        for scheduling_type in techniques:
            if (example_name[1] == 0 and "pipe" in scheduling_type):
                continue
            print(f"\n{bcolors.OKCYAN}Testing {example_name} scheduling technique {scheduling_type} {bcolors.ENDC}")
            path_ssa_example = "{0}/{1}/reports/{1}.cpp_mem2reg_constprop_simplifycfg_die.ll".format(base_path, example_name[0])
            log.info("Parsing Crashfile {0}".format(path_ssa_example))
            ssa_parser = Parser(path_ssa_example, example_name[0], log)
            ssa_parser.draw_cdfg("{0}/{1}/test.pdf".format(base_path, example_name[0]))
            
            stype = scheduling_type.replace('_rconst','')
            
            #handle alap by running asap first
            try:
                if scheduling_type == "alap":

                    blockprint(args)
                    scheduler = Scheduler(ssa_parser, "asap", log=log)
                    scheduler.create_scheduling_ilp()
                    status = scheduler.solve_scheduling_ilp(base_path, example_name[0])
                    sink_svs = scheduler.get_sink_svs()

                    #some people's code can't really handle the existing parser being used but this is not part of the assignment
                    #recreate parser just in case
                    ssa_parser = Parser(path_ssa_example, example_name[0], log)
                    # ssa_parser.draw_cdfg("{0}/{1}/test.pdf".format(base_path, example_name[0]))
                    scheduler = Scheduler(ssa_parser, "alap", log=log)
                    scheduler.create_scheduling_ilp(sink_svs)
                    results[example_name[0]][scheduling_type]["alap"] = alap_test(scheduler, sink_svs)
                    
                    enableprint()

                elif "pipe" in scheduling_type:
                    blockprint(args)
                    scheduler = Scheduler(ssa_parser, stype, log=log)
                    scheduler.create_scheduling_ilp(II=1)
                    enableprint()

                #all other stuff
                else:
                    blockprint(args)
                    scheduler = Scheduler(ssa_parser, stype, log=log)
                    scheduler.create_scheduling_ilp()
                    if scheduling_type == "asap":
                        ssa_parser.draw_cdfg("{0}/{1}/test_Asap.pdf".format(base_path, example_name[0]))
                    enableprint()
                    
            except Exception as e:
                error(f"Failed to run the scheduler due to an exception. Scheduling technique: {scheduling_type}")
                error(f"error msg {e}")
                results[example_name[0]][scheduling_type]["snode"]   = bcolors.FAIL + "Crash " + bcolors.ENDC
                results[example_name[0]][scheduling_type]["ddep"]    = bcolors.FAIL + "Crash " + bcolors.ENDC
                results[example_name[0]][scheduling_type]["interbb"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                results[example_name[0]][scheduling_type]["objfun"]  = bcolors.FAIL + "Crash " + bcolors.ENDC
                results[example_name[0]][scheduling_type]["alap"]    = bcolors.FAIL + "Crash " + bcolors.ENDC
                enableprint()
                continue
            
            # #add resource contraint
            # if "rconst" in scheduling_type:
            #     blockprint(args)
            #     ilp, constraints, obj_function = [scheduler.ilp, scheduler.constraints, scheduler.obj_fun]
            #     resource_manager = Resources(ssa_parser, { 'add' : 1 , 'mul' : 1}, log=log)
            #     resource_manager.add_resource_constraints_sdc(ilp, constraints, obj_function)
            #     enableprint()
                
            #these tests are universal and dont require an ILP solution, wrap them with try in case the solution is bad enough to make them raise an exception
            #true/false depending on test result, 1 if test crashed
            try:
                results[example_name[0]][scheduling_type]["snode"] = supernode_test(scheduler, args)
            except Exception as e:
                results[example_name[0]][scheduling_type]["snode"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                error(f"Supernode test crashed with msg {e}")
                
            try:
                results[example_name[0]][scheduling_type]["ddep"] = data_dependency_test(scheduler)
            except Exception as e:
                results[example_name[0]][scheduling_type]["ddep"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                error(f"Data dependency test crashed with msg {e}")
                    
            try:
                results[example_name[0]][scheduling_type]["interbb"] = inter_bb_dep_test(scheduler)
            except Exception as e:
                results[example_name[0]][scheduling_type]["interbb"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                error(f"Inter-BB dependency test crashed with msg {e}")
                    
            try:
                results[example_name[0]][scheduling_type]["objfun"] = obj_fun_test(scheduler, scheduling_type)
            except Exception as e:
                results[example_name[0]][scheduling_type]["objfun"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                error(f"Objective function test crashed with msg {e}")
            
            #run regular pipeline test
            if  scheduling_type == "pipelined" and example_name[1]:
                status = 0
                ii = 0
                scheduler = 0
                #prevent console spam
                
                # log.setLevel(logging.ERROR)
                while(status != 1 and ii <args.iimax+1):
                    ii= ii + 1
                    log.info(f"Trying II = {ii}")
                    blockprint(args)
                    ssa_parser = Parser(path_ssa_example, example_name[0], log)
                    scheduler = Scheduler(ssa_parser, stype, log=log)
                    scheduler.create_scheduling_ilp(II=ii)
                    ilp, constraints, obj_function = [scheduler.ilp, scheduler.constraints, scheduler.obj_fun]
                    enableprint()
                    status = scheduler.solve_scheduling_ilp(base_path, example_name[0])
                    
                # log.setLevel(logging.INFO)
                if status != 1:
                    error(f"Pipelined test failed after reaching II={args.iimax}")
                    results[example_name[0]][scheduling_type]["pipe"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                else:
                    #run pipeline check
                    try:
                        results[example_name[0]][scheduling_type]["pipe"] = pipeline_check(scheduler, ii)
                        hashes[example_name[0]][scheduling_type] = dict_hash(scheduler.ilp.get_ilp_solution())
                    except Exception as e:
                        results[example_name[0]][scheduling_type]["pipe"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                        error(f"Pipelined scheduler test crashed with msg {e}")
                    
            #run pipeline + resource constraint test
            elif scheduling_type == "pipelined_rconst" and example_name[1]:
                status = 0
                ii = 0
                scheduler = 0

                
                for mul in range(1,4):
                    for add in range(1,4):
                        for zext in range(1,4):
                            successful = False
                            while(not successful and ii <args.iimax+1):
                                ii= ii + 1
                                log.info(f"Trying II = {ii}")
                                blockprint(args)
                                ssa_parser = Parser(path_ssa_example, example_name[0], log)
                                scheduler = Scheduler(ssa_parser, stype, log=log)
                                scheduler.create_scheduling_ilp(II=ii)

                                resource_dict = { "mul":mul, "add":add, "zext":zext}

                                resource_manager = Resource_Manager(ssa_parser, scheduler.pass_scheduling_ilp, log=log)
                                resource_manager.add_resource_constraints(resource_dict)
                                
                                status = scheduler.solve_scheduling_ilp(base_path, example_name[0])

                                if status == 1:
                                    successful = resource_manager.check_resource_constraints_pipelined(resource_dict, ii)
                                enableprint()
                                
                            
                            if status != 1:
                                error(f"Pipelined test failed after reaching II={args.iimax}")
                                error(f"Resource constrained pipeline test failed mul {mul} add {add} zext {zext}")
                                results[example_name[0]][scheduling_type]["pipe"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                            else:
                                #run pipeline check
                                try:
                                    results[example_name[0]][scheduling_type]["pipe"] = pipeline_check(scheduler, ii)
                                    results[example_name[0]][scheduling_type]["rconst"] = resource_constraint_test(scheduler, { "mul":mul, "add":add, "zext":zext} )
                                    #reference hashes are computed using these
                                    if mul == 1 and add == 1 and zext == 1:
                                        hashes[example_name[0]][scheduling_type] = dict_hash(scheduler.ilp.get_ilp_solution())
                                except Exception as e:
                                    results[example_name[0]][scheduling_type]["pipe"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                                    results[example_name[0]][scheduling_type]["rconst"] = results[example_name[0]][scheduling_type]["pipe"]
                                    error(f"Resource constrained pipelined scheduler test crashed with msg{e}")
                                
            
            #solve ilp and test regular resource consrtraints when appropriate
            elif "rconst" in scheduling_type:
                for mul in range(1,4):
                    for add in range(1,4):
                        for zext in range(1,4):
                            try:
                                blockprint(args)
                                ssa_parser = Parser(path_ssa_example, example_name[0], log)
                                scheduler = Scheduler(ssa_parser, stype, log=log)
                                scheduler.create_scheduling_ilp()
                                
                                ilp_dependency_inj = scheduler.pass_scheduling_ilp
                                resource_manager = Resource_Manager(ssa_parser, ilp_dependency_inj, log=log)

                                resouce_constraint_dict = {}
                                resouce_constraint_dict["add"] = add
                                resouce_constraint_dict["mul"] = mul
                                resouce_constraint_dict["zext"] = zext

                                resource_manager.add_resource_constraints(resouce_constraint_dict)

                                status = scheduler.solve_scheduling_ilp(base_path, example_name[0])

                                results[example_name[0]][scheduling_type]["rconst"] = resource_constraint_test(scheduler, { "mul":mul, "add":add, "zext":zext} )
                            except Exception as e:
                                results[example_name[0]][scheduling_type]["rconst"] = bcolors.FAIL + "Crash " + bcolors.ENDC
                                error(f"Resource constrained scheduler test crashed with msg{e}")
                enableprint()
                                
                #reference hash for the resource constrainted asap scheduler has no zext contraint, calculate solution for add = mul = 1          
                try:
                                blockprint(args)
                                ssa_parser = Parser(path_ssa_example, example_name[0], log)
                                scheduler = Scheduler(ssa_parser, stype, log=log)
                                scheduler.create_scheduling_ilp()

                                ilp_dependency_inj = scheduler.pass_scheduling_ilp
                                resource_manager = Resource_Manager(ssa_parser, ilp_dependency_inj, log=log)

                                resource_manager.add_resource_constraints({ "mul":1, "add":1 })
                                
                                status = scheduler.solve_scheduling_ilp(base_path, example_name[0])
                                hashes[example_name[0]][scheduling_type] = dict_hash(scheduler.ilp.get_ilp_solution())
                                enableprint()
                except Exception as e:
                    error(f"Tried to solve the scheduling problem using the resource constrained ASAP scheduler but got the exception: {e}")
                                
            #not resource constrained, solve and add hash to dict 
            else:
                try:
                    blockprint(args)
                    scheduler.solve_scheduling_ilp(base_path, example_name[0])
                    hashes[example_name[0]][scheduling_type] = dict_hash(scheduler.ilp.get_ilp_solution())
                    enableprint()
                except Exception as e:
                    error(f"Tried to solve the ilp problem got the exception: {e}")
                
                
            if bcolors.FAIL + "Crash " + bcolors.ENDC not in results[example_name[0]][scheduling_type].values() and bcolors.FAIL + "Failed" + bcolors.ENDC not in results[example_name[0]][scheduling_type].values():
                success("All tests passed\n")
                
            elif False in results[example_name[0]][scheduling_type].values():
                warning("Not all tests completed successfully, might be due to the objective function being correct but not matching a known pattern, examine manually\n")
            
            elif bcolors.FAIL + "Crash " + bcolors.ENDC in results[example_name[0]][scheduling_type].values():
                error("One or more tests crashed, something is very wrong with the code\n")
    # success("Summary of all test results")
    print(f"{bcolors.WARNING}Kernel name                 Scheduling technique     Supernode test     Data dependency test     Inter-BB dependency test     Objective function test     Resource constraint test     Pipeline constraint test ALAP constraint test{bcolors.ENDC}")
    
    for example_name in kernels:
        for scheduling_type in techniques:
            if (example_name[1] == 0 and "pipe" in scheduling_type):
                continue
            # print(results[example_name[0]][scheduling_type])
            print("{:<28} {:<24} {:<27} {:<33} {:<37} {:<39} {:<37} {:<33} {:<34}".format(example_name[0],\
                    scheduling_type,\
                    results[example_name[0]][scheduling_type]["snode"],\
                    results[example_name[0]][scheduling_type].get('ddep'),\
                    results[example_name[0]][scheduling_type].get('interbb'), \
                    results[example_name[0]][scheduling_type].get('objfun'), \
                    results[example_name[0]][scheduling_type].get('rconst', bcolors.HEADER + "------" + bcolors.ENDC), \
                    results[example_name[0]][scheduling_type].get('pipe', bcolors.HEADER + "------" + bcolors.ENDC), \
                    results[example_name[0]][scheduling_type].get('alap', bcolors.HEADER + "------" + bcolors.ENDC)))
            
    print()
    print(f"\n{bcolors.OKBLUE} Comparisons of the scheduling results obtained from the student's code with known good solutions:")
    print(f"{bcolors.OKBLUE} A mismatch in this section doesn't necessarily imply that the code is wrong")
    for kernel in hashes.keys(): #iterate kernels tested 
        if(kernel not in refhashes.keys()):
            error(f"Kernel {kernel} not found in reference hash list, skipping check")
            continue
        for tech in hashes[kernel].keys(): #iterate scheduling techniques
           
            if hashes[kernel][tech] != refhashes[kernel][tech]:
                error(f"Hash obtained from the student's scheduler ({hashes[kernel][tech]}) for kernel {kernel}({tech})does not match the reference hash ({refhashes[kernel][tech]})")
            else:
                gerror(f"Hash obtained from the student's scheduler for kernel {kernel}({tech}) matches reference value")
    
    #reset print colors
    print(f'\033[0m')
                

       
#checks if constraints enforcing a given dictionary are present
def alap_test(scheduler, sink_delays):
    if scheduler.sched_tech != "alap":
        error(f"ALAP constraint test called but the scheduler is configured for another scheduling technique {scheduler.sched_tech}")
        return bcolors.FAIL + "Failed" + bcolors.ENDC
    print(sink_delays)
    print(len(sink_delays))

    #get all LEQ constraints with only one variable
    consts = [n.toDict() for n in scheduler.constraints.get_constraints().values() if len(n.toDict()["coefficients"]) == 1 and n.toDict()["sense"] == -1]
    print(consts)
    #number of constraints found, should be equal to the number of sinks
    found = 0
    for ssink in sink_delays:
        for const in consts:
            print(const["coefficients"][0]['name'])
            if const["coefficients"][0]["name"] == "sv"+ssink and abs(const["constant"]) == sink_delays[ssink]:
                log.info(f"Found ALAP constraint for ssink {ssink}: {const}")
                found = found +1

    if found != len(sink_delays):
        error(f"ALAP test failed, {len(sink_delays)} supersinks were given but only {found} constraints were found")
        error(f"sink_delays dictionary {sink_delays}")
        return bcolors.FAIL + "Failed" + bcolors.ENDC
    else:
        gerror("ALAP test passed")
        return bcolors.OKGREEN + "Passed" + bcolors.ENDC


def supernode_test(scheduler, args):
    for id_ in range(len(scheduler.cfg)):
        log.info(f"Checking BB {id_}")
        ssinkname = f"ssink_{id_}"
        ssourcename = f"ssrc_{id_}"
        sinktemp = [n for n in get_cdfg_nodes(scheduler.cdfg) if (n.attr['type'] == 'supersink' and int(n.attr['id']) == id_) ]
        
        #check the number of supersinks in BB
        if(len(sinktemp) > 1):
            error(f"Supernode test failed: More than one supersink in BB{id_}")
            print(temp)
            # print(temp[0]
            return bcolors.FAIL + "Failed" + bcolors.ENDC
        
        #conditionally check if the ssink was named correctly like explained in the assignment
        if args.no_name_check == 0:
            if(str(sinktemp[0]) == ssinkname):
                ssink = sinktemp[0]
            else:
                error(f"Supernode test failed: supersink should be named {ssinkname} but got {sinktemp[0]}")

        sourcetemp = [n for n in get_cdfg_nodes(scheduler.cdfg) if (n.attr['type'] == 'supersource' and int(n.attr['id']) == id_)]
        #check number of supernodes in BB
        if(len(sourcetemp) > 1):
            error(f"Supernode test failed: More than one supersource in BB{id_}")
            return bcolors.FAIL + "Failed" + bcolors.ENDC
        
        #conditionally check if the ssrc was named correctly like explained in the assignment
        if args.no_name_check == 0:
            if(str(sourcetemp[0]) == ssourcename):
                ssrc = sourcetemp[0]
            else:
                error(f"Supernode test failed: supersource should be named {ssourcename} but got {sourcetemp[0]}")
        
        #ssrc shouldnt have predecessors but should have at least one successor
        #ignore connections to other supernodes if requested
        if args.no_snode_conn:
            pred = [n for n in scheduler.cdfg.in_neighbors(sourcetemp[0] ) if (n.attr['type'] != 'supersink' and n.attr['type'] != 'supersource')]
            succ = [n for n in scheduler.cdfg.out_neighbors(sourcetemp[0] )if (n.attr['type'] != 'supersink' and n.attr['type'] != 'supersource')]
        else:
            pred = scheduler.cdfg.in_neighbors(sourcetemp[0] )
            succ = scheduler.cdfg.out_neighbors(sourcetemp[0])
        
        #supersource should have successors but not predecessors
        if(len(pred) > 0):
            error(f"Supernode test failed: {sourcetemp[0]} has predecessors but it should not : {pred}")
            return bcolors.FAIL + "Failed" + bcolors.ENDC

        if(len(succ) == 0):
            error(f"Supernode test failed: {sourcetemp[0]} has no successors but it should : {succ}")
            return bcolors.FAIL + "Failed" + bcolors.ENDC
        
        #supersink should have predecessors but no successors
        if args.no_snode_conn:
            pred = [n for n in scheduler.cdfg.in_neighbors(sinktemp[0] ) if (n.attr['type'] != 'supersink' and n.attr['type'] != 'supersource')]
            succ = [n for n in scheduler.cdfg.out_neighbors(sinktemp[0] )if (n.attr['type'] != 'supersink' and n.attr['type'] != 'supersource')]
        else:
            pred = scheduler.cdfg.in_neighbors(sinktemp[0] )
            succ = scheduler.cdfg.out_neighbors(sinktemp[0])
            
         #ssrc shouldnt have predecessors but should have at least one successor
        if(len(succ) > 0):
            error(f"Supernode test failed: {sinktemp[0]} has successors but it should not : {succ}")
            return bcolors.FAIL + "Failed" + bcolors.ENDC

        if(len(pred) == 0):
            error(f"Supernode test failed: {sinktemp[0]} has no predecessors but it should : {pred}")
            return bcolors.FAIL + "Failed" + bcolors.ENDC
        
    gerror("Artificial node test passed")
    return bcolors.OKGREEN + "Passed" + bcolors.ENDC

#checks if all the necessary data dependencies are added by the scheduler
def data_dependency_test(scheduler):
    #get constraints and nodes
    constraints = scheduler.constraints.get_constraints()
    nodes = get_cdfg_nodes(scheduler.cdfg)


    # horrible O(n*m*l) loop but the examples aren't very large
    #for every node - successor pair check if there is a constraint, fail if one is missing
    for node in nodes:
        latency = get_node_latency(node.attr)
        # print(f"\ncurrent node {node} {latency}")
        #only check successors in the same bb, ignore back edges 
        successors = [n for n in scheduler.cdfg.out_neighbors(node) if (n.attr['bbID'] == node.attr['bbID']) and (scheduler.cdfg.get_edge(node, n).attr["style"] != "dashed")]

        for successor in successors:
            # print(f"current successor {successor}")
            found = 0
            for constraint in constraints.values():
                """
                p predecessor l current
                4 possible ways to add constraints, match each with regex
                1: sv(l) - sv(p) >= L(p)   ^sv[a-zA-Z0-9_.]+ - sv[a-zA-Z0-9_.]+ >= [0-9]
                2: -sv(p) + sv(l) >= L(p)  ^-sv[a-zA-Z0-9_.]+ \+ sv[a-zA-Z0-9_.]+ >= [0-9]
                3: sv(p) - sv(l) <= -L(p)  ^sv[a-zA-Z0-9_.]+ - sv[a-zA-Z0-9_.]+ <= -[0-9]
                4: -sv(l) + sv(p) <= -L(p) ^-sv[a-zA-Z0-9_.]+ \+ sv[a-zA-Z0-9_.]+ <= -[0-9]
                """
                constdic = constraint.toDict()
                #0 == equals constraint, not relevant
                if constdic["sense"] == 0:
                    continue

                if len(constdic["coefficients"]) > 2:
                    error(f'Constraint {constraint} has more than 2 variables, this is not allowed')
                    return bcolors.FAIL + "Failed" + bcolors.ENDC

                #check the coefficients of the constraint, the coeffs of nodes can only be 1 or -1 and only the RHS can contain a different number
                for pair in constdic["coefficients"]:
                    if pair["value"] != 1 and pair["value"] != -1:
                        error(f'Variable {pair["name"]} in constraint {constraint} has illegal coefficient. Refer to the lecture slides, the coefficients of the nodes can only be 1 or -1')
                        return bcolors.FAIL + "Failed" + bcolors.ENDC

                succ = ""
                cur=""
                #pulp moves the constant to the left hand side, mult with -1
                const = -constdic["constant"]

                #greater/equal, types 1 and 2
                if constdic["sense"] == 1:
                    #type 1
                    if constdic["coefficients"][0]["value"] == 1:
                        succ = constdic["coefficients"][0]["name"]
                        cur = constdic["coefficients"][1]["name"]

                    #type 2
                    elif constdic["coefficients"][0]["value"] == -1:
                        succ = constdic["coefficients"][1]["name"]
                        cur = constdic["coefficients"][0]["name"]

                #less than/equal, types 3 and 4
                if constdic["sense"] == -1:
                    #type 3
                    if constdic["coefficients"][0]["value"] == 1:
                        succ = constdic["coefficients"][0]["name"]
                        cur = constdic["coefficients"][1]["name"]
                    #type 4
                    if constdic["coefficients"][0]["value"] == -1:
                        succ = constdic["coefficients"][1]["name"]
                        cur = constdic["coefficients"][0]["name"]

                #the constant can be negative too if the one above matches
                if(cur == f"sv{str(node)}" and succ == f"sv{str(successor)}" and int(const) == int(latency) ):
                    # print(f'Found constraint {string} for node {node} and successor {successor}')
                    found = 1
                    break

            if(found == 0):
                error(f'Data dependency test failed: Couldn\'t find constraint for node {node} and successor {successor}')
                return bcolors.FAIL + "Failed" + bcolors.ENDC

    gerror("Data dependency test passed")
    return bcolors.OKGREEN + "Passed" + bcolors.ENDC

def resource_constraint_test(scheduler, rdic):
    if scheduler.sched_sol == None:
        error("Resource constraint test requires a scheduling solution but none was given")
        return bcolors.FAIL + "Failed" + bcolors.ENDC
    
    ssinks = [n for n in get_cdfg_nodes(scheduler.cdfg) if n.attr['type'] == 'supersink']
    
    for ssink in ssinks:
        cycles = int(scheduler.ilp.get_operation_timing_solution(ssink)) 
        # print(ssink)
        for cycle in range(0,cycles+1):
            # print(cycle)
            nodes = scheduler.ilp.get_variables_solution(cycle)
            if scheduler.sched_tech == " pipelined" and (cycle-II>=0):
                nodes += scheduler.ilp.get_variables_solution(cycle-II)
            for rtype in rdic:
                n = [scheduler.cdfg.get_node(n) for n in nodes if (scheduler.cdfg.get_node(n).attr['type'] == rtype and scheduler.cdfg.get_node(n).attr['id'] == ssink.attr['id'] )]
                # print(f"{n} {rdic[rtype]} {cycle}")
                if len(n) > rdic[rtype]:
                    error(f"Resource constraint failed. Expected at most {rdic[rtype]} op(s) of type {rtype} in cycle {cycle} but found {len(n)}")
                    return bcolors.FAIL + "Failed" + bcolors.ENDC
                
    gerror(f"Resource constraint test passed. Resource dictionary: {rdic}")
    return bcolors.OKGREEN + "Passed" + bcolors.ENDC
    
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text             

#returns bcolors.FAIL + "Failed" + bcolors.ENDC if there are inter bb dependencies
def inter_bb_dep_test(scheduler):
    constraints = scheduler.constraints.get_constraints().values()
    nodes = get_cdfg_nodes(scheduler.cdfg)
    err = bcolors.FAIL + "Failed" + bcolors.ENDC
    for constraint in constraints:
        constdic = constraint.toDict()
        constops = [remove_prefix(n["name"], "sv") for n in constdic["coefficients"]]
        # print(constops)

        if "II" in constops:
            continue

        if len(constops) >2:
            error("More than two variables found in constraint, this is not allowed.")
            return err

        if len(constops) == 1:
            #check if we are dealing with an ALAP bound constraint
            valid = 0
            for node in get_cdfg_nodes(scheduler.cdfg):
                 if str(node) == constops[0] and node.attr["type"] == "supersink":
                    valid = 1
                    break
            if valid == 0:
                error(f"Less than two variables found in non-II, non-ALAP bound constraint {constraint}, this is not allowed.")
                return err
            else:
                continue

        if len(constops) == 0:
            error(f"No variabled found in {constraint}, this is not allowed.")
            return err

        # print(f"looking for {op1} {op2}")

        #get nodes returns iterator so it has to be called every time to make the loop run more than once
        for node in get_cdfg_nodes(scheduler.cdfg):
            if str(node) == constops[0]:
                node1 = node
                # print(f"node1 {node1}")
            elif str(node) == constops[1]:
                node2 = node
                # print(f"node2 {node2}")
        try:
            #supernodes aren't supposed to be in BBs so skip them
            if(node1.attr["type"] == "supersource" or node1.attr["type"] == "supersink" or node2.attr["type"] == "supersource" or node2.attr["type"] == "supersink"):
                continue
            if(node1.attr['bbID'] != node2.attr['bbID']):
                error(f"Constraint {constraint} contains nodes {node1} {node1.attr['bbID']} & {node2} {node2.attr['bbID']} which do not belong to the same BB")
                return bcolors.FAIL + "Failed" + bcolors.ENDC
        except:
            error(f"Inter BB test couldnt find nodes in constraint {constraint}")
            err = True
        
    if err == True:
        return bcolors.FAIL + "Failed" + bcolors.ENDC

    gerror("Inter-BB dependency test passed")
    return bcolors.OKGREEN + "Passed" + bcolors.ENDC

"""
checks obj fun against hardcoded known patterns, warn user if there's a mismatch
ASAP/pipelined:
minimise the sum of all nodes or just the sinks(add nodes with coeff=1)

ALAP:
either set ilp minimize=false and add everything with coeff=1 like asap or
add all nodes or sinks with coeff=-1
                
This if going to be a convoluted mess of ifs                
"""
def obj_fun_test(scheduler, scheduling_type):
    variables = [str(i) for i in list(scheduler.obj_fun.function_coeff.keys())]
    coeffs = scheduler.obj_fun.function_coeff.values()
    nvars = len(variables)
    nodes = [n for n in list(get_cdfg_nodes(scheduler.cdfg)) if(n.attr["type"] != "supersink" and n.attr["type"] != "supersource")]
    nnodes = len(nodes)
    nbbs = len(list(get_cdfg_nodes(scheduler.cfg)))
    warn = 0
    
    #first look at the numbers to speculate what the student might have done(all nodes in obj fun or just supernodes)
    allnodes = allnodeswithsuper = 0;
    if(nvars == nnodes):
        allnodes = 1
        log.info("Expecting all normal CDFG nodes to be in the objective function")
    elif(nvars == nnodes + nbbs*2):
        log.info("Expecting all CDFG nodes to be in the objective function")
        allnodeswithsuper = 1
    elif (nvars<nbbs):
        error("Number of variables in the objective function is less than the number of normal nodes. The objective function is not valid")
        warn = 1
    else:
        warning("Number of variables in objective function does not match any known patterns(More variables in objective function than there are normal nodes in the CDFG). Validity cannot be verified")
        warn = 1
        
    log.info(f'{nvars} variables in obj fun, {nnodes} nodes in CDFG, {nbbs} BBs')
    
    #check the coeffs
    #only case where the coeffs should be -1
    if scheduling_type == "alap" and scheduler.ilp.model_minimize == True:
        for coeff in coeffs:
            if(coeff != -1):
                warning(f'Warning: was expecting -1 but got {coeff} (ALAP)')
                warn = 1
         
    #in all other cases the coeffs should be 1
    else:
        for coeff in coeffs:
            if(coeff != 1):
                warning(f'Warning: was expecting 1 but got ({coeff}) ')
                warn = 1
    
    #check the variables
    
    
    if allnodes == 1:
        for node in nodes:
            string = "sv" + str(node)
            if string not in variables:
                warning(f'Warning: expecting all normal CDFG nodes to be in the obj fun but {string} is not')
                warn = 1

    elif allnodeswithsuper == 1:
        for node in get_cdfg_nodes(scheduler.cdfg):
            string = "sv" + str(node)
            if string not in variables:
                warning(f'Warning: expecting all normal CDFG nodes to be in the obj fun but {string} is not')
                warn = 1
    
    if(warn == 0):
        gerror("Objective function matched one of the known good patterns")
        return bcolors.OKGREEN + "Passed" + bcolors.ENDC
    else:
        yerror("Objective function didn't match one of the known good patterns, verify manually")
        print(f" List of ILP variables: \n{variables}\n")
        print(f" Objective function: \n{str(scheduler.obj_fun.get_obj_function())}\n")  
        return bcolors.FAIL + "Failed" + bcolors.ENDC
    
    
def pipeline_check(scheduler, ii_expected):
    try:
        II_var = scheduler.II
        assert II_var is not None
    except AssertionError as e:
        error("II variable is None")
        return bcolors.FAIL + "Failed" + bcolors.ENDC
             
    #get phis 
    phis = [n for n in scheduler.cdfg if n.attr ['type'] == 'phi']
    print(phis)
    for phi in phis:
        #get predecessors of phis, only consider back edges
        preds = [n for n in scheduler.cdfg.in_neighbors(phi) if n.attr['type'] != 'br' and scheduler.cdfg.get_edge(n, phi).attr["style"] == "dashed"]

        #each predecessor needs an II related constraint like in lecture 4 p93
        for pred in preds:
            foundCorrect = False
            foundIncorrect = False
            for const in scheduler.constraints.get_constraints().values():
                constdic = const.toDict()
                '''
                type 1:  svphi  - svpred >= L(pred) - ii_expected
                type 2: -svpred + svphi  >= L(pred) - ii_expected
                type 3: -svphi  + svpred <=  ii_expected-L(pred)
                type 4:  svpred - svphi  <=  ii_expected-L(pred)

                '''
                #0 == equals constraint, not relevant
                if constdic["sense"] == 0:
                    continue

                if len(constdic["coefficients"]) > 2:
                    error(f'Constraint {constraint} has more than 2 variables, this is not allowed')
                    return bcolors.FAIL + "Failed" + bcolors.ENDC

                val_const = -constdic["constant"]

                #greater/equal, types 1 and 2
                if constdic["sense"] == 1:
                    compval = get_node_latency(pred.attr) - ii_expected
                    #type 1
                    if constdic["coefficients"][0]["value"] == 1:
                        phiconst = constdic["coefficients"][0]["name"]
                        predconst = constdic["coefficients"][1]["name"]

                    #type 2
                    elif constdic["coefficients"][0]["value"] == -1:
                        phiconst = constdic["coefficients"][1]["name"]
                        predconst = constdic["coefficients"][0]["name"]

                #less than/equal, types 3 and 4
                if constdic["sense"] == -1:
                    compval = ii_expected-get_node_latency(pred.attr)
                    #type 3
                    if constdic["coefficients"][0]["value"] == -1:
                        phiconst = constdic["coefficients"][0]["name"]
                        predconst = constdic["coefficients"][1]["name"]

                    #type 4
                    elif constdic["coefficients"][0]["value"] == 1:
                        phiconst = constdic["coefficients"][1]["name"]
                        predconst = constdic["coefficients"][0]["name"]

                if(phiconst == f"sv{phi}" and predconst == f"sv{pred}" and int(val_const) == (compval)):
                    log.info(f"Found correct pipeline constraint for {phi} and {pred}")
                    foundCorrect = True
                    break
                
                combo1 = phiconst == f"sv{phi}" and predconst == f"sv{pred}"
                combo2 = phiconst == f"sv{pred}" and predconst == f"sv{phi}"
                if(combo1 or combo2):
                    foundIncorrect = True
                    
                
            if not foundCorrect:
                if foundIncorrect:
                    error(f"Found pipeline constraint for {phi} and {pred}, but it was not correct")
                else:
                    error(f"Pipeline constraint test failed: couldn't find pipeline constraint for {phi} and {pred}")
                return bcolors.FAIL + "Failed" + bcolors.ENDC
                
    gerror("Pipeline constraint test passed")
    return bcolors.OKGREEN + "Passed" + bcolors.ENDC
    
def find_node(scheduler, name):
    for node in get_cdfg_nodes(scheduler.cdfg):
            if str(node) == name:
                return node
            
def warning(msg):
    log.warning(f"{bcolors.WARNING}{msg}{bcolors.ENDC}")
   
#green error message, for test passed messages
def gerror(msg):
    print(f"{bcolors.OKGREEN}{msg}{bcolors.ENDC}")
    
#yellow error message, for obj fun warnings
def yerror(msg):
    log.error(f"{bcolors.WARNING}{msg}{bcolors.ENDC}")

def error(msg):
    log.error(f"{bcolors.FAIL}{msg}{bcolors.ENDC}")
    
def success(msg):
    log.info(f"{bcolors.OKGREEN}{msg}{bcolors.ENDC}")


# Disable
def blockprint(args):
    if args.no_print_suppress == False:
        sys.stdout = open(os.devnull, 'w')

# Restore
def enableprint():
    sys.stdout = sys.__stdout__
    
if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="This is the automated test script for the first assignment of SDC 202X",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # arg_parser.add_argument('--kernels', type=str, help='The list of kernels that the tester should use, all kernels are used when this is not specified')
    arg_parser.add_argument('--kernels', type=str, help='Space-separated list of kernels to be used for tests. Each kernel is followed by a comma and a number indicating whether it should be used for pipelined tests. 0 means no pipeline tests will be run and 1 means pipeline tests will be run. Example: "kernel_1,0 kernel_3,1"')
    arg_parser.add_argument('--methods', type=str, help='Space-separated list of scheduling methods that the tester should test, all methods are tested when this is not specified')
    arg_parser.add_argument('--iimax', type=int, help='The maximum II value that will be tested before the pipelined test automatically fails', default=40)
    arg_parser.add_argument("-v", '--verbose',  help='Makes the tester print detailed information',  action='store_true')
    arg_parser.add_argument('--no-name-check',  help='Do not check if the BBs were named properly',  action='store_true')
    arg_parser.add_argument('--no-snode-conn',  help='Do not check if the supernodes are connected or not',  action='store_true')
    arg_parser.add_argument('--no-print-suppress',  help="Do suppress prints from the student's code",  action='store_true')
    args = arg_parser.parse_args()
    main(args)
