import numpy as np
import numpy.linalg as la

from solver.Optimizer.BaseOptimizer import BaseOptimizer


class Simplex(BaseOptimizer):

    def __init__(self, A, b, c):
        super().__init__(A, b, c)

        self.B = None
        self.B_inv = None
        self.B_index = None

    # TODO: how to find initial basic feasible solution in other cases
    def find_init_basis(self):
        B_index = list(range(self.n - self.m, self.n))
        return B_index

    # TODO: consider the following cases
    # degeneracy
    # infeasible
    # infinity
    def solve(self):
        B_index = self.find_init_basis()
        A = self.A
        b = self.b
        c = self.c
        m = self.m
        n = self.n

        while True:

            CB = c[B_index]  # C_B
            B = A[:, B_index]  # B matrix
            B_inv = la.inv(B)  # B^{-1}
            XB = B_inv * b  # X_B
            z = CB.T * XB  # z

            # optimality computations
            r = [(i, c[i] - CB.T * B_inv * A[:, i]) for i in range(n) if i not in B_index]
            enter_index, enter_check = r[0]
            for i in range(1, len(r)):
                if enter_check > r[i][1]:
                    enter_index, enter_check = r[i]

            if enter_check > 0:
                break

            # Feasibility computations
            try:
                theta = XB / (B_inv * A[:, enter_index])
            except RuntimeWarning:  # inf is legal
                pass

            out_index = int(np.argmin(np.where(theta > 0, theta, INF)))

            # reindex
            B_index = [i if i != B_index[out_index] else enter_index for i in B_index]

        solution = np.mat(np.zeros((n, 1)))
        for i in range(m):
            solution[B_index[i], 0] = XB[i]

        self.B = B
        self.B_inv = B_inv
        self.B_index = B_index
        self.solution = solution
        self.optimal_value = z
        self.dual = CB.T * B_inv
