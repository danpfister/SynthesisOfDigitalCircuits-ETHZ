If you are reading this, you are probably in need of information regarding the first project of the course, "Synthesis of Digital Circuits". This documents briefly describes how to use the script "run_SDC.py" and use the automated tester.

run_SDC runs your scheduler implementation and generates a scheduling diagram for all HLS kernels specified in the input list(filelist.lst if nothing was specified by the user). These kernels are stored in the examples folder, do not delete or alter these files. The script tries out all scheduling methods unless told otherwise. The argument --methods can be used to control which scheduling techniques should be run and can accept multiple techniques in the form of a space-separated list.

The following scheduling techniques can be specified:
"asap", "alap", "asap_rconst", "pipelined", "pipelined_rconst"

Example, ASAP only:

python3 run_SDC.py --methods asap

Example, ASAP and resource constrained pipelined ASAP scheduling:

python3 run_SDC.py --methods "asap pipelined_rconst"


The usage of the tester is equally straightforward and can be run by executing "/opt/sdc-tester/tester.py" in the terminal. The tester tried to test the code in the src folder under the current directory your terminal is in. For instance, if your terminal is in /some/dir and you run the tester, it will try to test the scheduler in /some/dir/src. Like run_SDC, the tester tests all scheduling technique and kernel combinations by default which can be controlled using arguments. The kernels that should be used for testing can be specified with the --kernels argument, which takes a space-separated list of kernels. Each kernel is accompanied by a comma and either a 1 or 0 depending on whether the kernel contains loops and therefore can be used for pipeline tests.

Example: only test kernel 1(no loops)

/opt/sdc-tester/tester.py --kernels "kernel1,0"

Example: test kernel 1(no loops) and kernel 4 (constains a for loop)

/opt/sdc-tester/tester.py --kernels "kernel1,0 kernel4,1"

The tester will still work if the wrong number is given. However, depending on the kernel, the pipeline tests will either not run at all or fail due to missing pipeline constraints(which is expected from a non-loop kernel and a correctly written scheduler)

The scheduling techniques can be specified in the same way as described above. The only difference is that the tester doesn't accept the technique "all".

The tester will try to iteratively raise the II value until your code can generate a valid schedule while running the pipeline tests. The test will fail automatically if an II of 40 has been reached but no solution was found. This limit can be changed using the --iimax argument.
