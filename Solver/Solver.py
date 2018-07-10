import numpy as np
import numpy.linalg as la
from collections import defaultdict

from DataStructure import *


class LpSolver(object):
    """
    Using Revised Simplex Method
    standard form:
        max cx
        s.t. Ax <= b
    """

    def __init__(self):
        # objective type
        # 0 for init
        # 1 for max (standard)
        # 2 for min
        self.obj_type = 0

        # objective function
        self.objective = None

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

        # matrix format
        self.A = None
        self.b = None
        self.c = None

    def add_variable(self, name=None, index=None, lb=0, ub=INF):
        if not name:
            name = "var"
        elif name == "var":
            print("'var' is built-in name, rename your variable")
            return None

        index = index if index else self.variables_index
        if (name, index) in self.variables_collector.keys():
            print(name + " " + str(index) + " is used before")
            return None

        var = Variable(name=name, index=index, lb=lb, ub=ub)

        self.variables_collector[name][index] = var
        self.variables_index2variable[self.variables_index] = (name, index)
        self.variables_variable2index[(name, index)] = self.variables_index
        self.variables_index += 1
        return var

    # TODO(optimize): the input format should be checked
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
            var = Variable(name=name, index=i, lb=lb, ub=ub)

            vars_dict[i] = var
            self.variables_index2variable[self.variables_index] = (name, i)
            self.variables_variable2index[(name, i)] = self.variables_index
            self.variables_index += 1
        self.variables_collector[name].update(vars_dict)
        return vars_dict

    def add_constraint(self, constraint=None, name=None, index=None):
        if not name:
            name = "constr"
        elif name == "constr":
            print("'constr' is built-in name, rename your constraint")
            return None

        index = index if index else self.constraints_index

        if name != "constr" and index in self.constraints_collector[name].keys():
            print(name + " " + str(index) + " already exists in model")
            return None

        if isinstance(constraint, Constraint):
            # check whether variables exist in model
            if self._variable_check(constraint):
                return None
            self.constraints_collector[name][index] = constraint
            self.constraints_constraint2index[(name, index)] = self.constraints_index
            self.constraints_index2constraint[self.constraints_index] = (name, index)
            self.constraints_index += 1
            return constraint
        else:
            print(str(type(constraint)) + " can't be added as constraint")
            return None

    def add_constraints(self, constraints=None, name=None, index=None):
        if not name:
            name = "constr"
        elif name == "constr":
            print("'constr' is built-in name, rename your constraint")
            return None

        if not index:
            print("Please specify the index for constraints")
            return None

        # check whether variables exist in model
        for constr in constraints:
            if self._variable_check(constr):
                return None

        if len(index) == len(constraints):
            constrs_dict = dict()
            for i, constr in enumerate(constraints):
                if isinstance(constr, Constraint):
                    constrs_dict[index[i]] = constr
                    self.constraints_index2constraint[self.constraints_index] = (name, index[i])
                    self.constraints_constraint2index[(name, index[i])] = self.constraints_index
                    self.constraints_index += 1
                else:
                    print(str(type(constr)) + " can't be added as constraint")
                    return None
            self.constraints_collector[name].update(constrs_dict)
            return constrs_dict
        else:
            print("Wrong index input")
            print(len(index))
            print(len(constraints))
            return None

    def set_objective(self, obj, obj_type=MINIMIZE):
        if isinstance(obj, Expression):
            if self._variable_check(obj):
                return None
            self.objective = obj
        else:
            print("Wrong expression for objective function")
        if obj_type in (MINIMIZE, MAXIMIZE):
            self.obj_type = obj_type
        else:
            print("Wrong objective type")

    def _variable_check(self, expr):
        """
        if there are any variables not in model, return True
        :param expr:
        :return:
        """
        if isinstance(expr, Expression):
            expr_list = expr.variable_list
        elif isinstance(expr, Constraint):
            expr_list = expr.expression
        else:
            print(str(type(expr)) + " can't be checked")
            return True

        variable_keys = self.variables_variable2index.keys()
        for name, index, coefficient in expr_list:
            if (name, index) not in variable_keys:
                print(name + " " + str(index) + " not in model")
                return True

        return False


if __name__ == "__main__":
    model = LpSolver()
    x = model.add_variable(name="x")
    y = model.add_variables(name="y", index=[(i, j) for i in range(2) for j in range(2)])
    print(model.variables_index)
    print(model.variables_collector)
    print(model.variables_variable2index)
    print(model.variables_index2variable)
    print(x)
    print(type(x))
    print(x.name)
    print(x.index)
    print(y)
    print(type(y[0, 0]))
    print(y[0, 0].name)
    print(y[0, 0].index)
    u = model.add_constraint(x + y[0, 0] <= 10, name="c", index=0)
    v = model.add_constraints(
        [y[i, j] > 4 for i in range(2) for j in range(2)],
        name="v", index=[(i, j) for i in range(2) for j in range(2)]
    )
    print(u)
    print(v)
    model.set_objective(x+y[0, 0], MAXIMIZE)
    print(model.objective)
    print(model.obj_type)
    print(sum([y[i, j] for i in range(2) for j in range(2)]))

