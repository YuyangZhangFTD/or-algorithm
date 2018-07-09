import numpy as np
import numpy.linalg as la
from Variable import Variable
from Constraint import Constraint
from Constant import *


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

        # variables_name(str) : variables_dict(dict)
        # variables_index : Variable
        # "x": dict()
        # (0,0): X_{0,0}
        self.variables_dict = dict()
        self.variables_dict["var"] = dict()

        # constraints_name(str) : constraints_dict(dict)
        # constraints_index : coefficient_list, comp_sign, comp_value
        # "u": dict()
        # (0,0): u_{0,0}
        self.constraints_dict = dict()

        # variable number counter
        self.variables_count = 0
        # variables collector
        self.variables_total = dict()

        self.constraints_count = 0
        self.constraints_total = dict()

        # # (name, index) : Variable
        # self.variables_index_dict = dict()

    def add_variable(self, name=None):

        if name:
            print("No variables name")
            name = "var" + str(self.variables_count)
            auto = True

        var = Variable(name=name, index=self.variables_count, auto=True)
        self.variables_total[name, self.variables_count] = var
        self.variables_dict["var"][self.variables_count] = var
        self.variables_count += 1
        return var

    def add_variables(self, name=None, variables_index=list()):
        # TODO: check duplicated variables, same name and duplicated index
        if len(variables_index) == 0:
            print("No variables added")
            return None

        if name:
            print("No variables name")
            name = "var" + str(self.variables_count)
            auto = True

        var = dict()
        for index in variables_index:
            var[tuple(index)] = Variable(name=name, index=index, auto=auto)
            # mark variable index
            self.variables_total[name, index] = self.variables_count
            self.variables_count += 1

        self.variables_dict[name] = var
        return var

    def add_constraint(self, constraint=None, name=None):

        if constraint:
            print("No constraint added")
            return None

        if name:
            print("No constraint name")
            name = "constr" + str(self.constraints_count)

        self.constraints_dict[name] = Constraint(constraint)

        return self.constraints_dict[name]

    def add_constraints(self):
        pass

    def set_objective(self, obj, obj_type="min"):

        if obj_type == "min" or obj == 1:
            self.obj_type = 1
        elif obj_type == "max" or obj == 2:
            self.obj_type = 2
        else:
            print("Wrong objective type")

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
    model.add_variables()
