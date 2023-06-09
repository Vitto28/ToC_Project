#!/usr/bin/env python3


import sys
from subprocess import Popen
from subprocess import PIPE
import re
import random
import os
import copy

gbi = 0
varToStr = ["invalid"]


def printClause(cl):
    print(map(lambda x: "%s%s" %
          (x < 0 and eval("'-'") or eval("''"), varToStr[abs(x)]), cl))


def gvi(name):
    global gbi
    global varToStr
    gbi += 1
    varToStr.append(name)
    return gbi


def gen_vars(nodes, edges, node_num, k):
    varMap = {}

    for i in range(0, node_num):
        # n_i = node i is present in the k-clique
        n = "n_" + str(i + 1)
        varMap[n] = gvi(n)

    # counter variables
    for i in range(0, node_num + 1):
        for j in range(0, k):
            n = "s_" + str(i) + "_" + str(j)
            varMap[n] = gvi(n)
        n = "s_" + str(i) + "_" + str(k)
        varMap[n] = gvi(n)

    return varMap


# === aux functions for clause generation ===

# takes s_n_k as input and returns clauses [a,b], [a,c]
# which is equivalent to (a v b) & (a v c)
def getClauses(counter):
    n = counter[0]
    k = counter[1]

    a = (n-1, k)
    b = n
    c = (n-1, k-1)
    return [[a, b], [a, c]]


def reduce(lst, idx):
    lst_copy = lst.copy()
    new_lst = []
    first_term = lst.pop(idx)

    if len(lst) == 0:
        return lst_copy

    for i in range(0, len(first_term)):
        if type(first_term[i]) is list:
            if type(lst) is list:
                result = first_term[i] + lst
            else:
                result = first_term.copy()
                result.append(lst)
        else:
            if type(lst) is list:
                result = lst.copy()
                result.append(first_term[i])
            else:
                result = [first_term[i], lst]

        new_lst.append(result)

    return new_lst


def replaceWithClauses(input, d):

    # if we have a tuple, get s(n-1, k), x_n, and s(n-1, k-1)
    # note that if n is 0, we are at the end, so dont retrieve anything
    if type(input) is tuple:
        if input[0] == 0 or input[1] == 0:
            return input, False
        else:
            cl = getClauses(input)
            return cl, False

    if type(input) is int:
        return input, False

    flag = False

    i = 0
    # size = len(input)
    while i < len(input) and not flag:

        term = input[i]
        result, rmv_brack = replaceWithClauses(term, d + 1)

        if rmv_brack:
            new_list = []
            j = 0
            while j < len(input):
                if j == i:
                    new_list.extend(result)
                else:
                    new_list.append(input[j])
                j += 1
            input = new_list.copy()
        else:
            input[i] = result

        if i > len(input):
            continue

        if type(result) is not list:
            i = i + 1
            continue

        def depth(L): return isinstance(L, list) and max(map(depth, L))+1
        d = depth(input)
        if d > 2 and i < len(input) and d > 0 and not rmv_brack:
            input = reduce(input, i)

        # check if further reductions are needed
        done = True
        j = 0
        while j < len(input) and done:
            clause = input[j]
            for k in range(0, len(clause)):
                el = clause[k]
                if type(el) is tuple and el[0] > 0 and el[1] > 0:
                    done = False
                    i = j
                    break
            j += 1

        if done:
            flag = True
            if d == 0:
                return input
        if d == 1 and done:
            break
    return input, flag

# === generate clauses ===


def gen_clauses(nodes, edges, k, vars):

    clauses = []
    node_num = len(nodes)
    
    for i in range(0, node_num):
        found = False
        for j in range(i + 1, node_num):
            for edge in edges:
                if nodes[i] in edge and nodes[j] in edge:
                    found = True
                    break
            if not found:
                # add condition
                # if there is no edge between nodes i and j, then node_i and node_j cannot
                # both be true at the same time
                var1 = -vars["n_" + str(i + 1)]
                var2 = -vars["n_" + str(j + 1)]
                clauses.append([var1, var2])

    # s_0_0 and s_n_k are always true
    var = vars["s_0_0"]
    clauses.append([var])
    var = vars["s_" + str(node_num) + "_" + str(k)]
    clauses.append([var])

    # s_0_j is false for i <= j <= k
    for j in range(0, k):
        var = -vars["s_0_" + str(j + 1)]
        clauses.append([var])

    # s_i_0 is true for 0 <= i <= n
    for i in range(0, node_num):
        var = vars["s_" + str(i + 1) + "_0"]
        clauses.append([var])

    # s_n_k is true when either:
    # a. at least k of x1...xn-1 are true, ie, s(n-1, j) is true
    # b. at least k-1 of x1...xn-1 are true and xn is true, ie, ( xn and s(n-1, k-1) ) is true

    # remember: a v (b & c) == (a v b) & (a v c)

    counter = getClauses((node_num, k))

    def createClauses(input):
        return replaceWithClauses(input, 0)[0]

    result = createClauses(counter)
    for clause in result:
        list = []
        for term in clause:
            if type(term) is tuple:
                list.append(vars["s_" + str(term[0]) + "_" + str(term[1])])
            if type(term) is int:
                list.append(vars["n_" + str(term)])
        clauses.append(list)
    return clauses


# A helper function to print the cnf header
def printHeader(n):
    global gbi
    return "p cnf {} {}".format(gbi, n)


# A helper function to print a set of clauses cls
def printCnf(cls):
    return "\n".join(map(lambda x: "%s 0" % " ".join(map(str, x)), cls))


def kClique(filename, k):
    nodes = []
    edges = []

    try:
        k = int(k)
    except ValueError:
        return nodes, edges, None, None, "K must be an integer"

    try:
        f = open(filename, "r")
    except IOError:
        return nodes, edges, None, None, "File does not appear to exist"
    for line in f:
        line = line.split()
        if line:
            if line[0] == "n":
                nodes.append(line[1])
            if line[0] == "e":
                edges.append((line[1], line[2]))

    # check input is valid
    num_nodes = len(nodes)
    num_edges = len(edges)
    max_num_edges = num_nodes * (num_nodes - 1) / 2

    # handle invalid input

    if k < 1:
        return nodes, edges, None, None, "K-clique size must be at least 1"

    if k > num_nodes:
        return nodes, edges, None, None, "Can't find a " + str(k) + "-clique in a " + str(num_nodes) + "-node graph"

    if len(edges) > max_num_edges:
        return nodes, edges, None, None, "Graph has more edges than is feasible for its number of nodes."

    # compute vars

    vars = gen_vars(nodes, edges, num_nodes, k)

    rules = gen_clauses(nodes, edges, k, vars)

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
    # Save output
    z3_res = res
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

        # Save the solution
        pos_vars = list(facts)
        return nodes, edges, z3_res, pos_vars, None
    
    return nodes, edges, z3_res, [], "Unsatisfiable: no " + str(k) + "-clique found in graph"


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
    k = sys.argv[2]

    _, _, z3_res, pos_vars, message = kClique(filename, k)

    # Print results
    if z3_res is not None:
        print(z3_res)
    if pos_vars is not None:
        for v in pos_vars:
            print(v)
    elif message is not None:
        print(message)
