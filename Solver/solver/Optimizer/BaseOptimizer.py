from solver.DataStructure.Constant import *


class BaseOptimizer(object):

    def __init__(self, A, b, c):
        self.A = A
        self.b = b
        self.c = c
        self.m, self.n = A.shape

        self.solution = None
        self.optimal_value = None
        self.dual = None

        self.solution = None
        self.optimal_value = None
        self.dual = None
        self.status = NOT_SOLVED
