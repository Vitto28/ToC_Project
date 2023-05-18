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


def varName(pigeon, hole):
    return "inHole({},{})".format(pigeon, hole)


def gvi(name):
    global gbi
    global varToStr
    gbi += 1
    varToStr.append(name)
    return gbi


def gen_vars(nodes, edges, node_num, k):
    # TODO
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


def gen_clauses(nodes, edges, k, vars):

    clauses = []

    node_num = len(nodes)
    for i in range(0, node_num):
        for j in range(i + 1, node_num):
            # print("looking for " +
            #       "(" + str(nodes[i]) + ", " + str(nodes[j]) + ")")
            for edge in edges:
                found = False
                if nodes[i] in edge and nodes[j] in edge:
                    # print(
                    #     "edge " + "(" + str(nodes[i]) + ", " + str(nodes[j]) + ")" + " exists!")
                    found = True
                    break
                # print(
                #     "edge " + "(" + str(nodes[i]) + ", " + str(nodes[j]) + ")" + " DNE!")
            if not found:
                # print("not found")
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

    # takes s_n_k as input and returns clauses [a,b], [a,c]
    # which is equivalent to (a v b) & (a v c)
    def getClauses(counter):
        # def findA(n, k):
        #     return n - 1, k, vars["s_" + str(n - 1) + "_" + str(k)]

        # def findB(n):
        #     return vars["n_" + str(n)]

        # def findC(n, k):
        #     return n - 1, k - 1, vars["s_" + str(n - 1) + "_" + str(k - 1)]

        n = counter[0]
        k = counter[1]

        a = (n-1, k)
        b = n
        c = (n-1, k-1)
        return [[a, b], [a, c]]

    counter = getClauses((node_num, k))
    # print(counter)

    # print(counter)

    def replaceWithClauses(input):
        # print()
        # print("inside replaceWith")
        # print("input is: " + str(input))  # (4,3)

        old_input = copy.deepcopy(input)

        if type(input) is tuple:
            # print("getting clauses, leaving replaceWith")
            # print()
            return getClauses(input)

        for i in range(0, len(input)):
            clause = input[i]
            # print(str(i) + "-th clause is: " + str(clause))  # [ (4,3), 5 ]

            if type(clause) is not int:
                input[i] = replaceWithClauses(clause)

                # for j in range(0, len(clause)):
                #     el = clause[j]
                #     print(str(j) + "-th element of clause is: " + str(el))

                #     if type(el) is tuple:
                #         new_el = replaceWithClauses(el)
                #         clause[j] = new_el

        # print("input before update")
        # print(input)

        # print("remember, input was:")
        # print(old_input)

        # print("input var is")
        # print(input)

        last_el = input[-1]
        new_list = input[:-1][0]
        # print("last_el is")
        # print(last_el)
        flag = False
        for i in range(0, len(new_list)):
            if type(last_el) is list:
                flag = True
                for el in last_el:
                    new_list[i].append(el)

            else:
                # print(new_list[i])
                new_list[i].append(last_el)
                # print(new_list[i])

        final_list = []

        if not flag:
            final_list = new_list

        if flag:
            for i in range(0, len(new_list)):
                new_list[i].reverse()
                last_el = [new_list[i].pop()]
                last_el.append(new_list[i].pop())
                new_list[i].append(last_el)
                # print(last_el)

            # print("\nnewlist")
            # print(new_list)
            # print()

            for i in range(0, len(new_list)):  # r2
                terms = new_list[i].pop()
                # print("new_list[i]")
                # print(new_list[i])
                # print("term is")
                # print(terms)
                for j in range(0, len(new_list[i])):
                    tmp = copy.deepcopy(new_list[i][j])
                    for term in terms:
                        tmp.append(term)
                    # tmp.append(term)
                    final_list.append(tmp)
                    # print()
                    # print("final list up to now")
                    # print(final_list)
                    # print()

                # print()
                # print(new_list)
                # print()

                # for j in range(0, len(new_list[i])):
                #     print("appending " + str(last_el) +
                #           " to " + str(new_list[i][j]))
                #     clause = new_list[i][j]
                #     clause.append(last_el)

        # print()
        # print("our final list is")
        # for el in final_list:
        #     print(el)
        # print()
        # print("newlist is")
        # print(new_list)
        for i in range(0, len(input)):
            input[i] = final_list[i]

        # print("leaving replaceWith")
        # print()

    my_clauses = replaceWithClauses(counter)
    print(my_clauses)

    # finished = False
    # temp_clauses = getClauses((node_num, k))
    # while not finished:
    #     for i in range(0, len(temp_clauses)):
    #         print(temp_clauses[i])
    #         for var in temp_clauses[i]:
    #             if type(var) is tuple:
    #                 tmp = getClauses(var)
    #                 temp_clauses[i] = tmp
    #     finished = True

    # for i in range(1, node_num + 1):
    #     for j in range(1, k + 1):
    #         # a = s(i-1, j)
    #         a = vars["s_" + str(i - 1) + "_" + str(j)]
    #         # b = x_i
    #         b = vars["n_" + str(i)]
    #         # c = s(i-1, j-1)
    #         c = vars["s_" + str(i - 1) + "_" + str(j - 1)]
    #         clauses.append([a, b])
    #         clauses.append([a, c])

    return clauses


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

    # check input is valid
    num_nodes = len(nodes)
    max_num_edges = num_nodes * (num_nodes - 1) / 2

    if k > num_nodes:
        print("Can't find a " + str(k) + "-clique in a " +
              str(num_nodes) + "-node graph")
        sys.exit(1)

    if len(edges) > max_num_edges:
        print("Graph has more edges than is feasible for its number of nodes.")
        sys.exit(1)

    vars = gen_vars(nodes, edges, num_nodes, k)
    # for var in vars:
    #     print(var, vars[var])

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
