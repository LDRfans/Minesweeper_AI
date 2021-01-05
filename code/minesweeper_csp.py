from cspbase import *
import itertools
import numpy as np
from propagators import *
import API

def csp_model(minesweeper):
    '''Initialize a csp model.
    '''

    csp = CSP("Minesweeper")

    # list of lists, same structure as board in minesweeper
    variables = []

    # Initialize all variables in board.
    for row in range(minesweeper.dim1):
        temp_row = []
        for col in range(minesweeper.dim2):
            name = str(row) + " " + str(col)
            if minesweeper.flag[row][col]:
                domain = [1]
            elif not np.isnan(minesweeper.state[row][col]):
                domain = [0]
            else:
                domain = [0,1]
            var = Variable(name, domain)
            temp_row.append(var)
            csp.add_var(var)
        variables.append(temp_row)

    # Initialize all constraints.
    # cons = [[name(str), [variable, variable,..], sum(int)], ...]
    cons = []
    unassign = []
    for row in range(minesweeper.dim1):
        for col in range(minesweeper.dim2):
            if not np.isnan(minesweeper.state[row][col]):
                variables[row][col].assign(0)
            elif minesweeper.flag[row][col]:
                variables[row][col].assign(1)
            else:
                unassign.append(variables[row][col])
            if not np.isnan(minesweeper.state[row][col]) and not minesweeper.state[row][col] == 0:
                surrounding = minesweeper.get_surrounding(row,col)
                scope = []
                sum1 = minesweeper.state[row][col]
                for x,y in surrounding:
                    if minesweeper.flag[x][y]:
                        sum1-=1
                    if np.isnan(minesweeper.state[x][y]) and not minesweeper.flag[x][y]:
                        scope.append(variables[x][y])
                name = str(row) + " " + str(col)
                if scope:
                    cons.append([name, scope, sum1])
    
    # for button in minesweeper.buttons:
    #     # Assign value to all known variables.
    #     if button.is_show():
    #         variables[button.x][button.y].assign(0)
    #     elif button.is_flag():
    #         variables[button.x][button.y].assign(1)
    #     else:
    #         unassign.append(variables[button.x][button.y])
    #     # Constraint info for a non-empty visible button.
    #     if button.is_show() and not button.value == 0:
    #         surrounding = minesweeper.get_surrounding_buttons(button.x, button.y)
    #         scope = []
    #         sum1 = button.value
    #         for sur in surrounding:
    #             if sur.is_flag():
    #                 sum1 -= 1
    #             if not sur.is_show() and not sur.is_flag():
    #                 scope.append(variables[sur.x][sur.y])
    #         name = str(button.x) + " " + str(button.y)
    #         # Avoid empty scope. (All surrounding buttons are either visible or flagged.)
    #         if scope:
    #             cons.append([name, scope, sum1])

    # end-game: give it a fixed # 20:
    # if len(unassign) <= 20:
    #     cons.append(["endgame", unassign, minesweeper.remaining_mines])

    # Sort cons by length of scope.
    cons.sort(key=lambda x: len(x[1]))
    # Reduce constraint's scope.
    # ex: c1=[v1,v2,v3], c2=[v1,v2] => reduce c1 to [v3]
    for i in range(len(cons)-1):
        con1 = cons[i]
        for j in range(i+1,len(cons)):
            con2 = cons[j]
            if set(con1[1]) == set(con2[1]):
                continue
            if set(con1[1]) & set(con2[1]) == set(con1[1]):
                con2[1] = list(set(con2[1]).difference(set(con1[1])))
                con2[2] = con2[2] - con1[2]

    # Sort cons by length of scope.
    cons.sort(key=lambda x: len(x[1]))
    # overlap cons, same structure as cons list: [[name(str), [variable, variable,..], sum(int)], ...]
    ol_cons = []
    # list of lists, with [{var, var, var...},{}...]
    ol_set = []
    ol_var = []

    # Add new constraints if two constraints has at least two same variables in scope.
    # Create a new variable for overlap variables.
    # ex: c1=[v1,v2,v3], c2=[v2,v3,v4] => add c3=[v1,v2v3], c4=[v2v3,v4]. v2v3 is a new variable.
    for i in range(len(cons)-1):
        con1 = cons[i]
        for j in range(i+1,len(cons)):
            con2 = cons[j]
            if set(con1[1]) == set(con2[1]):
                continue
            if 1 < len(set(con1[1]) & set(con2[1])):
                ol_vars = set(con1[1]) & set(con2[1])
                con1_vars = set(con1[1]) - ol_vars
                con2_vars = set(con2[1]) - ol_vars
                con1_sum = con1[2]
                con2_sum = con2[2]
                name = ""

                if not ol_vars in ol_set:
                    for i in ol_vars:
                        name += i.name + ", "
                    name = "(" + name + ")"
                    var = Variable(name, list(range(len(ol_vars)+1)))
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

    cons.extend(ol_cons)

    # Create Constraint object for constraint in cons list.
    for con in cons:
        constraint = Constraint(con[0],con[1])
        tuples = satisfy_tuples(con[1],con[2])
        constraint.add_satisfying_tuples(tuples)
        csp.add_constraint(constraint)

    return csp


def satisfy_tuples(scope, sum1):
    '''
    '''

    product_list = []
    for var in scope:
        product_list.append(var.domain())
    product = list(itertools.product(*product_list))
    tuples = []
    for tuple in product:
        if sum(tuple) == sum1:
            tuples.append(tuple)
    return tuples

def solve_by_step(minesweeper):
    is_assigned = False

    csp = csp_model(minesweeper)

    solver = BT(csp)
    solver.bt_search_MS(prop_GAC)
    for var in csp.get_all_vars():

        try:
            cell = var.name.split()
            row = int(cell[0])
            col = int(cell[1])
        except:
            # continue if it's not a vriable in board.
            # in board variable name's format: row, col
            continue

        if var.get_assigned_value() == 1:
            if not minesweeper.flag[row][col]:
                minesweeper.flag[row][col]=1
                solve_by_step(minesweeper)
        elif var.get_assigned_value() == 0:
            if np.isnan(minesweeper.state[row][col]):
                return row,col
    return is_assigned

