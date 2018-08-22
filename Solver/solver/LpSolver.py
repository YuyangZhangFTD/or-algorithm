import numpy as np
from collections import defaultdict

from .Structure import *
from .Optimizer.Simplex import Simplex


class LpSolver(object):
    """
    Using Revised Simplex Method
    standard form:
        max cx
        s.t. Ax <= b
    """

    def __init__(self, name=None):
        self.name = name if name is not None else "lp"

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
        # the variables which need to be standardized
        # {(name, index)}
        self.standardize_variables_set = set()

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

        # temporary attribute
        self.free_constraint_variable = dict()

        # matrix format
        self.A = None
        self.b = None
        self.c = None
        self.m = None
        self.n = None

        # model
        self.model = None

    def add_variable(self, name=None, index=None, lb=0, ub=INF):
        if lb >= ub:
            raise SolverError("lower bound must be less than upper bound")

        name = self._name_check(name, default_name="var", default_type=type(Variable))

        index = self.variables_index if index is None else index

        if (name, index) in self.variables_collector.keys():
            raise SolverError(name + " " + str(index) + " is used before")

        variable = Variable(name=name, index=index, lb=lb, ub=ub)

        self.variables_collector[name].update({index, variable})
        self.variables_index2variable[self.variables_index] = (name, index)
        self.variables_variable2index[(name, index)] = self.variables_index

        if lb != 0 or ub != INF:
            self.standardize_variables_set.add((name, index))

        self.variables_index += 1
        return variable

    # TODO(optimize): the input_A format should be checked
    def add_variables(self, name=None, index=None, lb=0, ub=INF):
        if lb >= ub:
            raise SolverError("lower bound must be less than upper bound")

        name = self._name_check(name, default_name="var", default_type=type(Variable))

        if not index:
            raise SolverError("index isn't specified for variables")

        vars_dict = dict()

        for i in index:
            variable = Variable(name=name, index=i, lb=lb, ub=ub)

            vars_dict[i] = variable
            self.variables_index2variable[self.variables_index] = (name, i)
            self.variables_variable2index[(name, i)] = self.variables_index
            self.variables_index += 1

            if lb != 0 or ub != INF:
                self.standardize_variables_set.add((name, index))

        self.variables_collector[name].update(vars_dict)
        return vars_dict

    def add_constraint(self, constraint=None, name=None, index=None):

        name = self._name_check(name, default_name="var", default_type=type(Constraint))

        index = self.constraints_index if index is None is None else index

        if name != "constr" and index in self.constraints_collector[name].keys():
            raise SolverError(name + " " + str(index) + " already exists in model")

        if isinstance(constraint, Constraint):
            # check whether variables exist in model
            if not self._variables_in_model(constraint):
                raise SolverError("There are some variables not in model")
            self.constraints_collector[name].update({index: constraint})
            self.constraints_constraint2index[(name, index)] = self.constraints_index
            self.constraints_index2constraint[self.constraints_index] = (name, index)
            self.constraints_index += 1
            return constraint
        else:
            raise SolverError(str(type(constraint)) + " can't be added as constraint")

    # TODO(optimize): the input_A format should be checked
    def add_constraints(self, constraints=None, name=None, index=None):

        name = self._name_check(name, default_name="var", default_type=type(Constraint))

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
            raise SolverError("Wrong index input_A")

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

    @staticmethod
    def _name_check(name, default_name=None, default_type=None):
        if name is None:
            name = default_name
        elif name == default_name:
            raise SolverError(default_name + " is built-in name")
        elif not isinstance(name, str):
            raise SolverError(str(default_type) + " name must be str")

        return name

    # overwrite getattribute
    # get attributes which are in self.model
    def __getattribute__(self, item):
        if item not in self.__dict__.keys():
            try:
                return self.model.__dict__[item]
            except KeyError:
                raise SolverError("LpSolver don't have attribute " + item)

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

        ub_dict = defaultdict(dict)  # store ub constraints

        for name, index in self.standardize_variables_set:

            variable = self.variables_collector[name][index]

            if variable.lower_bound == -INF:

                # free variable
                # -inf <= x <= inf
                # x = x' - x''
                # 0 <= x' <= inf
                # 0 <= x'' <= inf, auxiliary variable
                # TODO(optimize): use an equation to eliminate free variable
                if variable.upper_bound == INF:
                    auxiliary_variable = self.add_variable(
                        name="free_" + variable.name, index=variable.index
                    )
                    variable.standard_lb = 0
                    variable.standard_ub = INF
                    variable.auxiliary_variable_name = auxiliary_variable.name
                    variable.auxiliary_variable_index = auxiliary_variable.index
                    continue

                # -inf <= x <= c
                # x' = -x
                # -c <= x' <= inf
                else:
                    variable.standard_lb = -variable.upper_bound
                    variable.standard_ub = -variable.lower_bound
                    variable.standardize_mul = -1

            # c <= x <= inf/c
            # x' = x - lb
            # x' + lb = x
            # s * c * (x' + lb) = b
            # s * c * x' = b - s * c * lb
            # 0 <= x' <= inf/c
            if variable.standard_lb != 0:
                variable.standardize_add = variable.standard_lb
                variable.standard_lb = 0

            # 0 <= x <= ub
            # 0 <= x' <= INF, 0 <= x_s <= INF
            # add constraint: x' + x_s = ub
            if variable.standard_ub != INF:

                ub = variable.standard_ub
                variable.standard_ub = INF

                slack_variable = self.add_variable(name="slack")
                ub_constraint = variable + slack_variable == ub

                ub_constraint.standard_variable_list = ub_constraint.expression.to_list()
                ub_constraint.is_standard = True

                ub_dict["ub"][self.constraints_index] = ub_constraint
                self.constraints_constraint2index[("ub", self.constraints_index)] = self.constraints_index
                self.constraints_index2constraint[self.constraints_index] = ("ub", self.constraints_index)
                self.constraints_index += 1

        for name in self.constraints_collector.keys():

            for index, constraint in self.constraints_collector[name].items():

                b_update = 0

                for i, var in enumerate(constraint.expression.variables_list):

                    if (var[0], var[1]) in self.standardize_variables_set:

                        variable = self.variables_collector[var[0]][var[1]]

                        constraint.expression.variables_list[i] = (
                            var[0],
                            var[1],
                            var[2] * variable.standardize_mul,
                            variable.standard_lb,
                            variable.standard_ub
                        )

                        # coefficient * standardize_mul * standardize_add
                        b_update += var[2] * variable.standardize_mul * variable.standardize_add

                    else:
                        continue

                constraint.compare_value -= b_update

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
                    surplus_variable = self.add_variable(name="surplus")
                    constraint.expression -= surplus_variable
                    constraint.compare_operator = EQ
                elif constraint.compare_operator == EQ:
                    pass
                elif constraint.compare_operator == NE:
                    raise SolverNotImplementedError("Not equal operator haven't been implemented")
                else:
                    raise SolverError("Wrong operator in constraint")

                # coefficient * sign
                constraint.standard_variable_list = constraint.expression.to_list()
                constraint.is_standard = True

        self.constraints_collector.update(ub_dict)

    def _2_matrix(self):
        self.m, self.n = self.constraints_index, self.variables_index
        self.A = np.mat(np.zeros((self.m, self.n)))
        self.b = np.mat(np.zeros((self.m, 1)))
        self.c = np.mat(np.zeros((self.n, 1)))

        for v in self.objective.to_list():
            i = self.variables_variable2index[(v[0], v[1])]
            self.c[i] = v[2]

        for c_n, c_dict in self.constraints_collector.items():
            for c_i, c_v in c_dict.items():
                i = self.constraints_constraint2index[(c_n, c_i)]
                self.b[i] = c_v.compare_value
                for v_i, v in enumerate(c_v.to_list()):
                    j = self.variables_variable2index[(v[0], v[1])]
                    self.A[i, j] = v[2]

    def _assign_value(self):

        for index in range(self.variables_index):
            variable_name, variable_index = self.variables_index2variable[index]
            variable = self.variables_collector[variable_name][variable_index]
            variable.value = self.solution[index]

        for index in range(self.constraints_index):
            constraint_name, constraint_index = self.constraints_index2constraint[index]
            constraint = self.constraints_collector[constraint_name][constraint_index]
            constraint.dual = self.dual[0, index]

    def solve(self, method="simplex"):
        self._2_standard_form()
        self._2_matrix()
        if method == "simplex":
            solver = Simplex(self.A, self.b, self.c)
            solver.solve()
            self.model = solver

        if self.solution is not None and self.optimal_value is not None:
            self._assign_value()
            return self.status


if __name__ == "__main__":
    # model = LpSolver()
    # x = model.add_variable(name="x")
    # y = model.add_variables(name="y", index=[(i, j) for i in range(2) for j in range(2)])
    # print(model.variables_index)
    # print(model.variables_collector)
    # print(model.variables_variable2index)
    # print(model.variables_index2variable)
    # print(x)
    # print(type(x))
    # print(x.name)
    # print(x.index)
    # print(x.lower_bound)
    # print(x.upper_bound)
    # print(y)
    # print(type(y[0, 0]))
    # print(y[0, 0].name)
    # print(y[0, 0].index)
    # u = model.add_constraint(x + y[0, 0] <= 10, name="c", index=0)
    # v = model.add_constraints(
    #     [y[i, j] >= 4 for i in range(2) for j in range(2)],
    #     name="v", index=[(i, j) for i in range(2) for j in range(2)]
    # )
    # print(model.constraints_index)
    # k = model.add_constraint(
    #     sum([y[i, j] for i in range(2) for j in range(2)]) <= 10,
    #     name="k"
    # )
    # print(u)
    # print(v)
    # print(k)
    # print(model.constraints_collector)
    # c = y[0, 0] + y[0, 1]
    # print(type(c))
    # c += y[1, 1]
    # print(type(c))
    # d = c <= 4
    # print(type(d))
    # print(d.expression.to_list())
    # d.expression -= y[1, 0]
    # print(type(d))
    # print(d.expression.to_list())
    # model.set_objective(x+y[0, 0], MAXIMIZE)
    # print(model.objective)
    # print(model.objective_type)
    # print(sum([y[i, j] for i in range(2) for j in range(2)]))
    # model = LpSolver()
    # x = model.add_variable(name="x", lb=-10, ub=55)
    # y = model.add_variable(name="y", lb=-INF, ub=0)
    # c1 = model.add_constraint(3 * x + 2 * y >= 10, name="c", index=1)
    # for item in model.constraints_collector.values():
    #     for tmp in item.values():
    #         print(tmp.expression.variables_list)
    #         print(tmp.compare_value)
    #         print(tmp.compare_operator)
    # print("*" * 100)
    # model._2_standard_form()
    # for item in model.constraints_collector.values():
    #     for tmp in item.values():
    #         print(tmp.expression.variables_list)
    #         print(tmp.compare_value)
    #         print(tmp.compare_operator)
    #         print(tmp.standard_variable_list)
    #         print(tmp.is_standard)
    # model = LpSolver("test")
    # x = model.add_variables(name="x", index=[i for i in range(1, 4)])
    # c1 = model.add_constraint(x[1] + 2 * x[2] + 2 * x[3] <= 20)
    # c2 = model.add_constraint(2 * x[1] + x[2] + 2 * x[3] <= 20)
    # c3 = model.add_constraint(2 * x[1] + 2 * x[2] + x[3] <= 20)
    # model.set_objective(-10 * x[1] - 12 * x[2] - 12 * x[3])
    # model._2_standard_form()
    # model._2_matrix()
    # model._simplex()
    model = LpSolver("test")
    x = model.add_variables(name="x", index=[1, 2])
    model.add_constraint(x[1] + 2 * x[2] <= 8)
    model.add_constraint(4 * x[1] <= 16)
    model.add_constraint(4 * x[2] <= 12)
    model.set_objective(2 * x[1] + 3 * x[2], obj_type=MAXIMIZE)
    # model._2_standard_form()
    # model._2_matrix()
    status = model.solve(method="simplex")
    print(status)
    print(model.solution)
