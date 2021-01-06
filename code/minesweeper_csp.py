import itertools
import numpy as np
from cspbase import *
from propagators import *
import API


def csp_model(minesweeper):
    csp = CSP("Minesweeper")

    variables = []
    for row in range(minesweeper.dim1):
        row_vars = []
        for col in range(minesweeper.dim2):
            identity = str(row) + " " + str(col)
            if minesweeper.flag[row][col]:
                domain = [1]
            elif not np.isnan(minesweeper.state[row][col]):
                domain = [0]
            else:
                domain = [0, 1]
            var = Variable(identity, domain)
            row_vars.append(var)
            csp.add_var(var)
        variables.append(row_vars)

    constrains = []
    unassigned = []
    for row in range(minesweeper.dim1):
        for col in range(minesweeper.dim2):
            if not np.isnan(minesweeper.state[row][col]):
                variables[row][col].assign(0)
            elif minesweeper.flag[row][col]:
                variables[row][col].assign(1)
            else:
                unassigned.append(variables[row][col])
            if not np.isnan(minesweeper.state[row][col]) and not minesweeper.state[row][col] == 0:
                surrounding = minesweeper.get_surrounding(row, col)
                scope = []
                mine_num = minesweeper.state[row][col]
                for x, y in surrounding:
                    if minesweeper.flag[x][y]:
                        mine_num -= 1
                    if np.isnan(minesweeper.state[x][y]) and not minesweeper.flag[x][y]:
                        scope.append(variables[x][y])
                identity = str(row) + " " + str(col)
                if scope:
                    constrains.append([identity, scope, mine_num])

    constrains.sort(key=lambda c: len(c[1]))

    for i in range(len(constrains) - 1):
        con1 = constrains[i]
        for j in range(i + 1, len(constrains)):
            con2 = constrains[j]
            if set(con1[1]) == set(con2[1]):
                continue
            if set(con1[1]) & set(con2[1]) == set(con1[1]):
                con2[1] = list(set(con2[1]).difference(set(con1[1])))
                con2[2] = con2[2] - con1[2]

    constrains.sort(key=lambda c: len(c[1]))
    ol_cons = []
    ol_set = []
    ol_var = []

    for i in range(len(constrains) - 1):
        con1 = constrains[i]
        for j in range(i + 1, len(constrains)):
            con2 = constrains[j]
            if set(con1[1]) == set(con2[1]):
                continue
            if 1 < len(set(con1[1]) & set(con2[1])):
                ol_vars = set(con1[1]) & set(con2[1])
                con1_vars = set(con1[1]) - ol_vars
                con2_vars = set(con2[1]) - ol_vars
                con1_sum = con1[2]
                con2_sum = con2[2]
                identity = ""

                if ol_vars not in ol_set:
                    for v in ol_vars:
                        identity += v.name + ", "
                    identity = "(" + identity + ")"
                    var = Variable(identity, list(range(len(ol_vars) + 1)))
                    csp.add_var(var)
                    ol_var.append(var)
                    ol_set.append(ol_vars)
                else:
                    index = ol_set.index(ol_vars)
                    var = ol_var[index]

                con1_vars.add(var)
                con2_vars.add(var)
                ol_cons.append(["", list(con1_vars), con1_sum])
                ol_cons.append(["", list(con2_vars), con2_sum])
    constrains.extend(ol_cons)

    for con in constrains:
        constraint = Constraint(con[0], con[1])
        tuples = satisfy_tuples(con[1], con[2])
        constraint.add_satisfying_tuples(tuples)
        csp.add_constraint(constraint)

    return csp


def satisfy_tuples(scope, mine_num):
    product_list = []
    for v in scope:
        product_list.append(v.domain())
    product = list(itertools.product(*product_list))
    tuples = []
    for t in product:
        if sum(t) == mine_num:
            tuples.append(t)
    return tuples


def cspPlayer(minesweeper):
    csp = csp_model(minesweeper)

    solver = BT(csp)
    solver.bt_search_MS(prop_BT)
    for var in csp.get_all_vars():
        try:
            cell = var.name.split()
            row = int(cell[0])
            col = int(cell[1])
        except:
            continue

        if var.get_assigned_value() == 1:
            if not minesweeper.flag[row][col]:
                minesweeper.flag[row][col] = 1
                # solve_by_step(minesweeper)
        elif var.get_assigned_value() == 0:
            if np.isnan(minesweeper.state[row][col]):
                return row, col
    return -1, -1
