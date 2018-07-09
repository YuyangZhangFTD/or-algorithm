import numbers

from Constant import *


class Variable(object):

    def __init__(self, name, index, lb=0, ub=INF):

        # if not specified, using "var"+str(solver.variable_index)
        self.name = name if name else None

        # if not specified, using solver.variable_index
        self.index = index if index else None

        # False for name or index being specified
        self.auto = True if name or index else False

        self.coefficient = 1
        self.sign = POSITIVE  # Expression record
        self.lower_bound = lb
        self.upper_bound = ub
        self.value = None

    def __add__(self, other):

        if isinstance(other, Variable) or isinstance(other, Expression):
            expr = Expression(variable=self)
            return expr + other
        else:
            print("'+' is not implemented between Variable and " + str(type(other)))
            return None

    def __sub__(self, other):
        if isinstance(other, Variable) or isinstance(other, Expression):
            return Expression(variable=self) - other
        else:
            print("'-' is not implemented between Variable and " + str(type(other)))
            return None

    def __mul__(self, other):
        if isinstance(other, numbers.Real):
            self.coefficient *= other
            return self
        else:
            print("Not supported type for " + str(type(other)))
            return None

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, numbers.Real):
            self.coefficient /= other

    def __rtruediv__(self, other):
        return self / other

    # TODO
    def __str__(self):
        return self.name + str(self.index)


class Expression(object):

    def __init__(self, variable=None):

        # [(variable_name, variable_index, variable_coefficient), ...]
        self.variable_list = list()

        # [POSITIVE, NEGATIVE, ...]
        self.sign_list = list()

        if isinstance(variable, Variable):
            self.variable_list.append((
                variable.name,
                variable.index,
                variable.coefficient
            ))
            self.sign_list.append(variable.sign)

    def __le__(self, other):

        return None

    def __lt__(self, other):

        return None

    def __ge__(self, other):

        return None

    def __gt__(self, other):

        return None

    def __eq__(self, other):

        return None

    def __neg__(self):

        self.sign_list = [-s for s in self.sign_list]
        return self

    def __add__(self, other):
        if isinstance(other, Variable):
            self.variable_list.append((other.name, other.index, other.coefficient))
            self.sign_list.append(other.sign)
            return self
        elif isinstance(other, Expression):
            self.variable_list += other.variable_list
            self.sign_list += other.sign_list
            return self
        else:
            print("'+' is not implemented between Expression and " + str(type(other)))
            return None

    def __sub__(self, other):
        if isinstance(other, Variable):
            self.variable_list.append((other.name, other.index, other.coefficient))
            self.sign_list.append(-1 * other.sign)
            return self
        elif isinstance(other, Expression):
            return self + (-other)
        else:
            print("'-' is not implemented between Expression and " + str(type(other)))
            return None

    def __mul__(self, other):
        if isinstance(other, numbers.Real):
            self.variable_list = list(map(lambda x: x[-1] * other, self.variable_list))
            return self
        else:
            print("'*' is not implemented between Expression and " + str(type(other)))
            return None

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, numbers.Real):
            self.variable_list = list(map(
                lambda x: (x[0], x[1], x[2] / other),
                self.variable_list
            ))
            return self
        else:
            print("'/' is not implemented between Expression and " + str(type(other)))
            return None

    def __rtruediv__(self, other):
        return self / other


class Constraint(object):

    def __init__(self, expression=None, operator=None, value=None):
        self.expression = expression
        self.compare_operator = operator
        self.compare_value = value


if __name__ == "__main__":
    a = Variable(name="x", index=(0, 0))
    b = Variable(name="x", index=(0, 1))
    c = Variable(name="x", index=(0, 2))
    d = Variable(name="y", index=3)
    e = 3 * (3 * a + b * 2) - (5 * c + 6 * d)
    print(a.coefficient)
    print(a)
    print(b.coefficient)
    print(c.coefficient)
    print(d.coefficient)
    print(d)
    print(isinstance(a + b, Expression))
    print(isinstance(e, Expression))
    print(e.variable_list)
    print(e.sign_list)
