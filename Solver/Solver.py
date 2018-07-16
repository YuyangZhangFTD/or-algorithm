import numpy as np
import numpy.linalg as la
from collections import defaultdict

from DataStructure import *
from Error import *


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
        self.objective_type = 0

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
        self.m = None
        self.n = None

        # temporary attribute
        self.variables_standard_dict = dict

    def add_variable(self, name=None, index=None, lb=0, ub=INF):
        if lb >= ub:
            raise SolverError("lower bound must be less than upper bound")

        if not name:
            name = "var"
        elif name == "var":
            raise SolverError("'var' is built-in name, rename your variable")

        index = index if index else self.variables_index
        if (name, index) in self.variables_collector.keys():
            raise SolverError(name + " " + str(index) + " is used before")

        var = Variable(name=name, index=index, lb=lb, ub=ub)

        self.variables_collector[name][index] = var
        self.variables_index2variable[self.variables_index] = (name, index)
        self.variables_variable2index[(name, index)] = self.variables_index
        self.variables_index += 1
        return var

    # TODO(optimize): the input format should be checked
    def add_variables(self, name=None, index=None, lb=0, ub=INF):
        if lb >= ub:
            raise SolverError("lower bound must be less than upper bound")

        if not name:
            name = "var"
        elif name == "var":
            raise SolverError("'var' is built-in name, rename your variable")

        if not index:
            raise SolverError("index isn't specified for variables")

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
            raise SolverError("'constr' is built-in name, rename your constraint")

        index = index if index else self.constraints_index

        if name != "constr" and index in self.constraints_collector[name].keys():
            raise SolverError(name + " " + str(index) + " already exists in model")

        if isinstance(constraint, Constraint):
            # check whether variables exist in model
            if not self._variables_in_model(constraint):
                raise SolverError("There are some variables not in model")
            self.constraints_collector[name][index] = constraint
            self.constraints_constraint2index[(name, index)] = self.constraints_index
            self.constraints_index2constraint[self.constraints_index] = (name, index)
            self.constraints_index += 1
            return constraint
        else:
            raise SolverError(str(type(constraint)) + " can't be added as constraint")

    def add_constraints(self, constraints=None, name=None, index=None):
        if not name:
            name = "constr"
        elif name == "constr":
            raise SolverError("'constr' is built-in name, rename your constraint")

        if not index:
            raise SolverError("Please specify the index for constraints")

        # check whether variables exist in model
        for constr in constraints:
            if not self._variables_in_model(constr):
                raise SolverError("There are some variables not in model")

        if len(index) == len(constraints):
            constrs_dict = dict()
            for i, constr in enumerate(constraints):
                if isinstance(constr, Constraint):
                    constrs_dict[index[i]] = constr
                    self.constraints_index2constraint[self.constraints_index] = (name, index[i])
                    self.constraints_constraint2index[(name, index[i])] = self.constraints_index
                    self.constraints_index += 1
                else:
                    raise SolverError(str(type(constr)) + " can't be added as constraint")
            self.constraints_collector[name].update(constrs_dict)
            return constrs_dict
        else:
            raise SolverError("Wrong index input")

    def set_objective(self, obj, obj_type=MINIMIZE):
        if isinstance(obj, Expression):
            if not self._variables_in_model(obj):
                raise SolverError("Variable not in model")
            self.objective = obj
        else:
            raise SolverError("Wrong expression for objective function")

        if obj_type in (MINIMIZE, MAXIMIZE):
            self.objective_type = obj_type
        else:
            raise SolverError("Wrong objective type")

    def _variables_in_model(self, expr):
        """
        if there are any variables not in model, return False
        :param expr:
        :return:
        """
        if isinstance(expr, Expression):
            expr_list = expr.variables_list
        elif isinstance(expr, Constraint):
            expr_list = expr.expression.variables_list
        else:
            raise SolverError((str(type(expr)) + " can't be checked"))

        variable_keys = self.variables_variable2index.keys()
        for name, index, coefficient, _, _ in expr_list:
            if (name, index) not in variable_keys:
                print(name + " " + str(index) + " not in model")
                return False

        return True

    def _2_standard_form(self):
        """
        1. recourse coefficients are non-negative
        2. objective is maximize
        3. constraints are equation
        4. decision variables are non-negative
        :return:
        """
        if self.objective_type == 2:
            self.objective_type = 1
            self.objective = -self.objective

        ub_dict = defaultdict(dict)

        for name in self.constraints_collector.keys():
            for index, constraint in self.constraints_collector[name].items():

                # x' = x - lb and x <= ub
                # var: (name, index, coefficient, lb, ub)
                for i, var in enumerate(constraint.expression.variables_list):

                    # temporary variable: tuple ===> list
                    var = list(var)

                    if var[3] == -INF:

                        # -inf <= x <= inf
                        # x = x' - x''
                        if var[4] == INF:
                            # TODO: to be implemented
                            raise SolverNotImplementedError("No constraint variable is not supported now")

                        # -inf <= x <= c
                        # x' = -x
                        # -c <= x' <= inf
                        else:
                            constraint.expression.sign_list[i] *= -1
                            var[3], var[4] = -var[4], -var[3]

                    # c <= x <= inf/c
                    # x' = x - lb
                    # x' + lb = x
                    # s * c * (x' + lb) = b
                    # s * c * x' = b - s * c * lb
                    # 0 <= x' <= inf/c
                    if var[3] != 0:
                        constraint.compare_value -= var[3] * var[2] * constraint.expression.sign_list[i]
                        var[4] = INF if var[4] == INF else var[4] - var[3]
                        var[3] = 0

                    # 0 <= x <= ub
                    # 0 <= x' <= INF, 0 <= x_s <= INF
                    # add constraint: x' + x_s = ub
                    if var[4] != INF:
                        slack_variable = self.add_variable(name="slack")
                        ub_constraint = self.variables_collector[var[0]][var[1]] + slack_variable == var[4]

                        # TODO: is there better way to format the variable bound in upper bound constraint?
                        ub_constraint.expression.variables_list[0] = (var[0], var[1], 1, 0, INF)
                        ub_constraint.standard_variable_list = ub_constraint.expression.to_list()
                        ub_constraint.is_standard = True

                        ub_dict["ub"][self.constraints_index] = ub_constraint
                        self.constraints_constraint2index[("ub", self.constraints_index)] = self.constraints_index
                        self.constraints_index2constraint[self.constraints_index] = ("ub", self.constraints_index)
                        self.constraints_index += 1
                        var[4] = INF

                    constraint.expression.variables_list[i] = tuple([var[i] for i in range(5)])

                if constraint.compare_value < 0:
                    constraint.compare_value *= -1
                    constraint.compare_operator *= -1
                    constraint.expression.variables_list = [
                        (tmp_x[0], tmp_x[1], tmp_x[2] * -1, tmp_x[3], tmp_x[4])
                        for tmp_x in constraint.expression
                    ]

                if constraint.compare_operator == LE:
                    slack_variable = self.add_variable(name="slack")
                    constraint.expression += slack_variable
                    constraint.compare_operator = EQ
                elif constraint.compare_operator == GE:
                    tightening_variable = self.add_variable(name="tightening")
                    constraint.expression -= tightening_variable
                    constraint.compare_operator = EQ
                elif constraint.compare_operator == EQ:
                    pass
                elif constraint.compare_operator == NE:
                    # TODO: to be implemented
                    raise SolverNotImplementedError("Not equal operator haven't been implemented")
                else:
                    raise SolverError("Wrong operator in constraint")

                # coefficient * sign
                constraint.standard_variable_list = constraint.expression.to_list()
                constraint.is_standard = True

        self.constraints_collector.update(ub_dict)


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
    print(x.lower_bound)
    print(x.upper_bound)
    print(y)
    print(type(y[0, 0]))
    print(y[0, 0].name)
    print(y[0, 0].index)
    u = model.add_constraint(x + y[0, 0] <= 10, name="c", index=0)
    v = model.add_constraints(
        [y[i, j] >= 4 for i in range(2) for j in range(2)],
        name="v", index=[(i, j) for i in range(2) for j in range(2)]
    )
    print(model.constraints_index)
    k = model.add_constraint(
        sum([y[i, j] for i in range(2) for j in range(2)]) <= 10,
        name="k"
    )
    print(u)
    print(v)
    print(k)
    print(model.constraints_collector)
    c = y[0, 0] + y[0, 1]
    print(type(c))
    c += y[1, 1]
    print(type(c))
    d = c <= 4
    print(type(d))
    print(d.expression.to_list())
    d.expression -= y[1, 0]
    print(type(d))
    print(d.expression.to_list())
    model.set_objective(x+y[0, 0], MAXIMIZE)
    print(model.objective)
    print(model.objective_type)
    print(sum([y[i, j] for i in range(2) for j in range(2)]))
    model = LpSolver()
    x = model.add_variable(name="x", lb=-10, ub=55)
    y = model.add_variable(name="y", lb=-INF, ub=0)
    c1 = model.add_constraint(3 * x + 2 * y >= 10, name="c", index=1)
    for item in model.constraints_collector.values():
        for tmp in item.values():
            print(tmp.expression.variables_list)
            print(tmp.compare_value)
            print(tmp.compare_operator)
    print("*" * 100)
    model._2_standard_form()
    for item in model.constraints_collector.values():
        for tmp in item.values():
            print(tmp.expression.variables_list)
            print(tmp.compare_value)
            print(tmp.compare_operator)
            print(tmp.standard_variable_list)
            print(tmp.is_standard)
