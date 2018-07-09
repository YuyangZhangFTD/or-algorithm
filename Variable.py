import numbers

from Constant import *


class Variable(object):

    def __init__(self, name, index, auto=False):

        self.auto = auto

        # variable name
        self.name = name

        # variable index
        self.index = index

        # 0 for init
        self.coef = 0

        # -1 for init
        self.next = []

        # -1 for init
        #  0 for leq
        #  1 for <
        #  2 for geq
        #  3 for >
        #  4 for =
        self.comp_sign = -1
        self.comp_value = None

    def __add__(self, other):
        self.next.append((other.name, other.index, other.coef))
        return self

    def __sub__(self, other):
        other.coef *= -1
        self.next.append(other.index)
        return self

    def __mul__(self, other):
        self.coef = other
        return self

    def __le__(self, other):
        self.comp_sign = 0
        self.comp_value = other
        return self

    def __lt__(self, other):
        self.comp_sign = 1
        self.comp_value = other
        return self

    def __ge__(self, other):
        self.comp_sign = 2
        self.comp_value = other
        return self

    def __gt__(self, other):
        self.comp_sign = 3
        self.comp_value = other
        return self

    def __eq__(self, other):
        self.comp_sign = 4
        self.comp_value = other
        return self


