from solver.DataStructure.DataStructure import Variable, Expression, Constraint
from solver.DataStructure.Constant import *
from solver.DataStructure.Error import *


def test_create_variable():
    x1 = Variable(name="x", index=1)
    assert x1.name == "x"
    assert x1.index == 1


def test_variable_add_sub():
    x1 = Variable(name="x", index=1)
    x2 = Variable(name="x", index=2)
    x3 = Variable(name="x", index=3)
    assert isinstance(x1 + x2 - x3, Expression)

    x2 += x1
    x3 -= x1
    assert isinstance(x2, Expression)
    assert isinstance(x3, Expression)


def test_variable_mul_div():
    x1 = Variable(name="x", index=1)
    assert x1.coefficient == 1
    x1 = Variable(name="x", index=1)
    x1 * 5
    assert x1.coefficient == 5
    x1 = Variable(name="x", index=1)
    x1 * 0
    assert x1.coefficient == 0
    x1 = Variable(name="x", index=1)
    x1 * -1
    assert x1.coefficient == -1
    x1 = Variable(name="x", index=1)
    x1 / 2
    assert x1.coefficient == 0.5
    x1 = Variable(name="x", index=1)
    x1 / -2
    assert x1.coefficient == -0.5


def test_variable_compare():
    x1 = Variable(name="x", index=1)
    assert isinstance(x1 <= 1, Constraint)
    assert isinstance(x1 >= 1, Constraint)
    assert isinstance(x1 == 1, Constraint)
