import time
import functools


class Variable:
    def __init__(self, name, domain=None):
        if domain is None:
            domain = []
        self.name = name
        self.dom = list(domain)
        self.curdom = [True] * len(domain)
        self.assignedValue = None

    def add_domain_values(self, values):
        for val in values:
            self.dom.append(val)
            self.curdom.append(True)

    def domain_size(self):
        return len(self.dom)

    def domain(self):
        return list(self.dom)

    def prune_value(self, value):
        self.curdom[self.value_index(value)] = False

    def unprune_value(self, value):
        self.curdom[self.value_index(value)] = True

    def cur_domain(self):
        values = []
        if self.is_assigned():
            values.append(self.get_assigned_value())
        else:
            for i, val in enumerate(self.dom):
                if self.curdom[i]:
                    values.append(val)
        return values

    def in_cur_domain(self, value):
        if value not in self.dom:
            return False
        if self.is_assigned():
            return value == self.get_assigned_value()
        else:
            return self.curdom[self.value_index(value)]

    def cur_domain_size(self):
        if self.is_assigned():
            return 1
        else:
            return sum(1 for v in self.curdom if v)

    def restore_curdom(self):
        for i in range(len(self.curdom)):
            self.curdom[i] = True

    def is_assigned(self):
        return self.assignedValue is not None

    def assign(self, value):
        self.assignedValue = value

    def unassign(self):
        if not self.is_assigned():
            print("ERROR")
            return
        self.assignedValue = None

    def get_assigned_value(self):
        return self.assignedValue

    def value_index(self, value):
        return self.dom.index(value)

    def __repr__(self):
        return ("Var-{}".format(self.name))

    def __str__(self):
        return ("Var--{}".format(self.name))


class Constraint:
    def __init__(self, name, scope):
        self.scope = list(scope)
        self.name = name
        self.sat_tuples = dict()
        self.sup_tuples = dict()

    def add_satisfying_tuples(self, tuples):
        for x in tuples:
            t = tuple(x)
            if t not in self.sat_tuples:
                self.sat_tuples[t] = True

            for i, val in enumerate(t):
                var = self.scope[i]
                if not (var, val) in self.sup_tuples:
                    self.sup_tuples[(var, val)] = []
                self.sup_tuples[(var, val)].append(t)

    def get_scope(self):
        return list(self.scope)

    def check(self, values):
        return tuple(values) in self.sat_tuples

    def get_n_unasgn(self):
        n = 0
        for v in self.scope:
            if not v.is_assigned():
                n = n + 1
        return n

    def get_unasgn_vars(self):
        vs = []
        for v in self.scope:
            if not v.is_assigned():
                vs.append(v)
        return vs

    def has_support(self, var, val):
        if (var, val) in self.sup_tuples:
            for t in self.sup_tuples[(var, val)]:
                if self.tuple_is_valid(t):
                    return True
        return False

    def tuple_is_valid(self, t):
        for i, var in enumerate(self.scope):
            if not var.in_cur_domain(t[i]):
                return False
        return True

    def __str__(self):
        return "{}({})".format(self.name, [var.name for var in self.scope])


class CSP:
    def __init__(self, name, vars=[]):
        self.name = name
        self.vars = []
        self.cons = []
        self.vars_to_cons = dict()
        for v in vars:
            self.add_var(v)

    def add_var(self, v):
        # if not type(v) is Variable:
        #     print("Trying to add non variable ", v, " to CSP object")
        # elif v in self.vars_to_cons:
        #     print("Trying to add variable ", v, " to CSP object that already has it")
        # else:
        self.vars.append(v)
        self.vars_to_cons[v] = []

    def add_constraint(self, c):
        for v in c.scope:
            if v not in self.vars_to_cons:
                return
            self.vars_to_cons[v].append(c)
        self.cons.append(c)

    def get_all_cons(self):
        return self.cons

    def get_all_vars(self):
        return list(self.vars)

class BT:
    def __init__(self, csp):
        self.csp = csp
        self.nDecisions = 0
        self.nPrunings = 0
        self.unasgn_vars = list()
        self.TRACE = False
        self.runtime = 0

    def trace_on(self):
        self.TRACE = True

    def trace_off(self):
        self.TRACE = False

    def clear_stats(self):
        self.nDecisions = 0
        self.nPrunings = 0
        self.runtime = 0

    # def print_stats(self):
    #     print("Search made {} variable assignments and pruned {} variable values".format(
    #         self.nDecisions, self.nPrunings))

    def restoreValues(self, prunings):
        for var, val in prunings:
            var.unprune_value(val)

    def restore_all_variable_domains(self):
        for var in self.csp.vars:
            if var.is_assigned():
                var.unassign()
            var.restore_curdom()

    def extractMRVvar(self):
        md = -1
        mv = None
        for v in self.unasgn_vars:
            if md < 0:
                md = v.cur_domain_size()
                mv = v
            elif v.cur_domain_size() < md:
                md = v.cur_domain_size()
                mv = v
        self.unasgn_vars.remove(mv)
        return mv

    def restoreUnasgnVar(self, var):
        self.unasgn_vars.append(var)

    def bt_search_MS(self, propagator):
        self.clear_stats()
        self.unasgn_vars = []
        for v in self.csp.vars:
            if not v.is_assigned():
                self.unasgn_vars.append(v)

        status, prunings = propagator(self.csp)  
        self.nPrunings = self.nPrunings + len(prunings)

        status = self.bt_recurse_MS(propagator, 1)  

        self.restoreValues(prunings)

        return self.nDecisions

    def bt_recurse_MS(self, propagator, level):

        if not self.unasgn_vars:
            return True
        else:
            var = self.extractMRVvar_MS()
            if not var:
                return True

            for val in var.cur_domain():
                var.assign(val)
                self.nDecisions = self.nDecisions + 1

                status, prunings = propagator(self.csp, var)
                self.nPrunings = self.nPrunings + len(prunings)
                if status:
                    if self.bt_recurse_MS(propagator, level + 1):
                        return True
                self.restoreValues(prunings)
                var.unassign()

            self.restoreUnasgnVar(var)
            return False

    def extractMRVvar_MS(self):
        for var in self.unasgn_vars:
            if var.cur_domain_size() == 1:
                self.unasgn_vars.remove(var)
                return var

        for con in self.csp.get_all_cons():
            if con.get_n_unasgn() == 0:
                continue
            if con.get_n_unasgn() == 1:
                mv = con.get_unasgn_vars()[0]
                self.unasgn_vars.remove(mv)
                return mv
        return None
