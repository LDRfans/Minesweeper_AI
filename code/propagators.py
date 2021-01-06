def prop_BT(csp, newVar=None):
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


def prop_FC(csp, newVar=None):
    pruned = []
    isDeadend = False

    if not newVar:
        cons = csp.get_all_cons()
        for con in cons:
            scope = con.get_scope()
            if len(scope) == 1:
                result = FCCheck(con, scope[0])
                pruned.extend(result[1])
                if not result[0]:
                    isDeadend = True
                    break

    cons = csp.get_all_cons()
    for con in cons:
        scope = con.get_scope()
        if con.get_n_unasgn() == 1:
            result = FCCheck(con, con.get_unasgn_vars()[0])
            pruned.extend(result[1])
            if not result[0]:
                isDeadend = True
                break
    if isDeadend:
        return (False, pruned)
    return (True, pruned)


def FCCheck(C, x):
    pruned = []
    cur_dom = x.cur_domain()
    for val in cur_dom:
        if not C.has_support(x, val):
            x.prune_value(val)
            pruned.append((x, val))

    if not x.cur_domain_size():
        return (False, pruned)
    return (True, pruned)


def prop_GAC(csp, newVar=None):
    queue = []
    pruned = []
    cons = csp.get_all_cons()

    if not newVar:
        queue = cons.copy()
    else:
        queue = csp.get_cons_with_var(newVar).copy()

    # For looping queue use an indicator count. It avoids keep append and
    # remove items in the queue list that may slow down the program.
    count = 0
    while count < len(queue):

        con = queue[count]
        scope = con.get_scope()

        for i in range(len(scope)):
            var = scope[i]
            curdom = var.cur_domain()
            found = False
            for val in curdom:
                if con.has_support(var, val):
                    continue
                else:
                    found = True
                    var.prune_value(val)
                    pruned.append((var, val))
                    if not var.cur_domain_size():
                        queue = []
                        return (False, pruned)

            if found:
                cons = csp.get_cons_with_var(var)
                for c in cons:
                    if c not in queue[count:]:
                        queue.append(c)
        count += 1

    return (True, pruned)
