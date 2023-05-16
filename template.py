#!/usr/bin/env python3


import sys
from subprocess import Popen
from subprocess import PIPE
import re
import random
import os

gbi = 0
varToStr = ["invalid"]


def printClause(cl):
    print(map(lambda x: "%s%s" %
          (x < 0 and eval("'-'") or eval("''"), varToStr[abs(x)]), cl))


def varName(pigeon, hole):
    return "inHole({},{})".format(pigeon, hole)


def gvi(name):
    global gbi
    global varToStr
    gbi += 1
    varToStr.append(name)
    return gbi


# def gen_vars(pigeons, holes):

#     varMap = {}

#     for hole in range(0, holes):
#         for pigeon in range(0, pigeons):
#             n = "inHole_"+str(pigeon)+"_"+str(hole)
#             varMap[n] = gvi(n)

#     # Insert here the code to add mapping from variable numbers to readable variable names.
#     # A single variable with a human readable name "var_name" is added, for instance, as follows:
#     # varMap["var_name"] = gvi("var_name")
#     # let's add another one.
#     # varMap["var2_name"] = gvi("var2_name")

#     return varMap


def gen_vars(nodes, edges):
    # TODO
    varMap = {}

    for edge in edges:
        n = "edge_" + edge[0] + "_" + edge[1] # TODO: Not relevant
        varMap[n] = gvi(n)

    return varMap


def genConstr(nodes, edges, k, vars):
    import math

    # TODO
    clauses = []
    return clauses


# def genPigConstr(pigeons, holes, vars):

#     clauses = []

#     # Insert here the code to generate the clauses.  A single clause var_name | var2_name is added as follows
#     # clauses.append( [   vars["var_name"],  vars["var2_name"]   ])

#     # Cond 1: A pigeon cannot be inside two holes
#     for pigeon in range(0, pigeons):
#         for hole in range(0, holes):
#             for other_hole in range(hole + 1, holes):
#                 var1 = -vars["inHole_"+str(pigeon)+"_"+str(hole)]
#                 var2 = -vars["inHole_"+str(pigeon)+"_"+str(other_hole)]
#                 clauses.append([var1, var2])

#     # Cond 2: Each hole can contain only one pigeon
#     for hole in range(0, holes):
#         for pigeon in range(0, pigeons):
#             for other_pigeon in range(pigeon + 1, pigeons):
#                 var1 = -vars["inHole_"+str(pigeon)+"_"+str(hole)]
#                 var2 = -vars["inHole_"+str(other_pigeon)+"_"+str(hole)]
#                 clauses.append([var1, var2])

#     # Cond 3: Each pigeon must stay inside some hole
#     # idea from a, b, c, at least one of them must be true
#     for pigeon in range(0, pigeons):
#         list = []
#         for hole in range(0, holes):
#             list.append(vars["inHole_"+str(pigeon)+"_"+str(hole)])
#         clauses.append(list)

#     return clauses


# A helper function to print the cnf header
def printHeader(n):
    global gbi
    return "p cnf {} {}".format(gbi, n)


# A helper function to print a set of clauses cls
def printCnf(cls):
    return "\n".join(map(lambda x: "%s 0" % " ".join(map(str, x)), cls))


# This function is invoked when the python script is run directly and not imported
if __name__ == '__main__':
    # if not (os.path.isfile(SATsolver) and os.access(SATsolver, os.X_OK)):
    # if Z3 is installed with homebrew in the PATH env no need to explicitly specify the solver
    #    print "Set the path to SATsolver correctly on line 4 of this file (%s)" % sys.argv[0]
    #    sys.exit(1)

    # This is for reading in the arguments.
    if len(sys.argv) != 3:
        print("Usage: %s <filename> <k>" % sys.argv[0])
        sys.exit(1)

    filename = sys.argv[1]
    k = int(sys.argv[2])

    nodes = []
    edges = []

    f = open(filename, "r")
    for line in f:
        line = line.split()
        if line[0] == "n":
            nodes.append(line[1])
        elif line[0] == "e":
            edges.append((line[1], line[2]))

    # vars = gen_vars(pigeons, holes)

    vars = gen_vars(nodes, edges)

    # rules = genPigConstr(pigeons, holes, vars)

    rules = genConstr(nodes, edges, k, vars)

    head = printHeader(len(rules))
    rls = printCnf(rules)

    # here we create the cnf file for SATsolver
    fl = open("tmp_prob.cnf", "w")
    fl.write("\n".join([head, rls]))
    fl.close()

    # this is for runing SATsolver
    ms_out = Popen(["z3 tmp_prob.cnf"], stdout=PIPE,
                   shell=True).communicate()[0]

    # SATsolver with these arguments writes the solution to a file called "solution".  Let's check it
    # res = open("solution", "r").readlines()
    res = ms_out.decode('utf-8')
    # Print output
    print(res)
    res = res.strip().split('\n')

    # if it was satisfiable, we want to have the assignment printed out
    if res[0] == "s SATISFIABLE":
        # First get the assignment, which is on the second line of the file, and split it on spaces
        # Read the solution
        asgn = map(int, res[1].split()[1:])
        # Then get the variables that are positive, and get their names.
        # This way we know that everything not printed is false.
        # The last element in asgn is the trailing zero and we can ignore it

        # Convert the solution to our names
        facts = map(lambda x: varToStr[abs(x)], filter(lambda x: x > 0, asgn))

        # Print the solution
        for f in facts:
            print(f)
