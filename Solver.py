import numpy as np
import numpy.linalg as la
from collections import defaultdict

from Constant import *
from DataStructure import *


def quick_sum(vars_list=list()):
    if len(vars_list) == 0:
        print("No available variables")
        return None
    tmp = vars_list[0]
    for i in range(1, len(vars_list)):
        tmp += vars_list[i]
    coefficient_list = tmp.next
    coefficient_list.inset(0, (tmp.name, tmp.index, tmp.coef))
    return coefficient_list


class LpSolver(object):
    """
    Using Revised Simplex Method
    standard form:
        min cx
        s.t. Ax >= b
    """

    def __init__(self):
        # objective type
        # 0 for init
        # 1 for min (standard)
        # 2 for max
        self.obj_type = 0

        # variables number counter
        self.variables_index = 0
        # variables collector
        # variables_name(str) : variables_dict(dict)
        # variables_index : Variable
        # "x": dict()
        # (0,0): X_{0,0}
        self.variables_collector = defaultdict(dict)
        # index 2 variable
        # index : (variable_name, variable_index)
        self.variables_index2variable = dict()
        # variable 2 index
        # (variable_name, variable_index) : index
        self.variables_variable2index = dict()

        # constraints number counter
        self.constraints_index = 0
        # constraints collector
        # constraints_name(str) : constraints_dict(dict)
        # constraints_index : coefficient_list, comp_sign, comp_value
        # "u": dict()
        # (0,0): u_{0,0}
        self.constraints_collector = defaultdict(dict)
        # index 2 constraint
        # index : (constraint_name, constraint_index)
        self.constraints_index2constraint = dict()
        # constraint 2 index
        # (constraint_name, constraint_index) : index
        self.constraints_constraint2index = dict()

    def add_variable(self, name=None, index=None, lb=0, ub=INF):
        if not name:
            name = "var"
        elif name == "var":
            print("'var' is built-in name, rename your variable")
            return None

        index = index if index else self.variables_index

        if (name, index) in self.variables_collector.keys():
            print(name+" "+str(index)+" is used before")
            return None

        var = Variable(name=name, index=index, lb=lb, ub=ub)
        self.variables_collector[name][index] = var
        self.variables_index2variable[self.variables_index] = (name, index)
        self.variables_variable2index[(name, index)] = self.variables_index
        self.variables_index += 1
        return var

    # TODO: optimize index input
    def add_variables(self, name=None, index=None, lb=0, ub=INF):
        if not name:
            name = "var"
        elif name == "var":
            print("'var' is built-in name, rename your variable")
            return None

        if not index:
            print("index isn't specified for variables")
            return None

        vars_dict = dict()

        for i in index:
            var = Variable(name=name, index=index, lb=lb, ub=ub)
            vars_dict[i] = var
            self.variables_index2variable[self.variables_index] = (name, i)
            self.variables_variable2index[(name, i)] = self.variables_index
            self.variables_index += 1
        self.variables_collector[name] = vars_dict
        return vars_dict

    def add_constraint(self, constraint=None, name=None):

        pass

    def add_constraints(self, constraints=None, name=None):

        pass

    def set_objective(self, obj, obj_type=MINIMIZE):
        if isinstance(obj, Expression):
            pass    # TODO
        else:
            print("Wrong expression for objective function")
        if obj_type in (MINIMIZE, MAXIMIZE):
            self.obj_type = obj_type
        else:
            print("Wrong objective type")

    # TODO
    def pre_check(self):
        if self.obj_type == 0:
            print("please set objective type")
            return False
        elif self.obj_type == 2:
            self.c *= -1
            self.obj_type = 1

        if not (
            self.c.shape[0] == 1 and
            self.b.shape[1] == 1 and
            self.c.shape[1] == self.A.shape[1] and
            self.A.shape[0] == self.b.shape[0]
        ):
            print("Wrong data matrix input")
            return False

        return True


if __name__ == "__main__":
    model = LpSolver()
    model.add_variable(name="x")
    model.add_variables(name="y", index=[(i, j) for i in range(5) for j in range(5)])
    print(model.variables_index)
    print(model.variables_collector)
    print(model.variables_variable2index)
    print(model.variables_index2variable)
