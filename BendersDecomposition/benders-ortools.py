import numpy as np
from collections import defaultdict
from ortools.linear_solver import pywraplp

example = 1

if example == 1:
    # example 1, optimal 350
    num_s = 4
    num_d = 3
    supply = [10, 30, 40, 20]
    demand = [20, 50, 30]
    c = np.array([
        [2, 3, 4],
        [3, 2, 1],
        [1, 4, 3],
        [4, 5, 2]
    ])
    f = np.array(
        [[10, 30, 20] for _ in range(4)]
    )
    bar_y = np.array([
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 0],
        [0, 1, 0]
    ])
elif example == 2:
    # example 2, optimal 4541
    num_s = 8
    num_d = 7
    supply = [20, 20, 20, 18, 18, 17, 17, 10]
    demand = [20, 19, 19, 18, 17, 16, 16]
    c = np.array([
        [31, 27, 28, 10, 7, 26, 30],
        [15, 19, 17, 7, 22, 17, 16],
        [21, 17, 19, 29, 27, 22, 13],
        [9, 19, 7, 15, 20, 17, 22],
        [19, 7, 18, 10, 12, 27, 23],
        [8, 16, 10, 10, 11, 13, 15],
        [14, 32, 22, 10, 22, 15, 19],
        [30, 27, 24, 26, 25, 15, 19]
    ])
    f = np.array([
        [649, 685, 538, 791, 613, 205, 467],
        [798, 211, 701, 506, 431, 907, 945],
        [687, 261, 444, 264, 443, 946, 372],
        [335, 385, 967, 263, 423, 592, 939],
        [819, 340, 233, 889, 211, 854, 823],
        [307, 620, 845, 919, 223, 854, 823],
        [560, 959, 782, 417, 358, 589, 383],
        [375, 791, 720, 416, 251, 887, 235]
    ])
    bar_y = np.array([
        [0, 1, 0, 0, 0, 0, 1],
        [0, 0, 1, 0, 0, 0, 0],
        [1, 1, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 1, 1, 1, 0]
    ])
else:
    print("Example not found")

M = np.ones((num_s, num_d))
for i in range(num_s):
    for j in range(num_d):
        M[i, j] = min(supply[i], demand[j])

params = dict()
params["num_s"] = num_s
params["num_d"] = num_d
params["supply"] = supply
params["demand"] = demand
params["c"] = c
params["f"] = f
params["M"] = M

'''
# ====================== solve problem directly ======================
# init solver
solver = pywraplp.Solver("test", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
# solver = pywraplp.Solver("test", pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
# solver = pywraplp.Solver("test", pywraplp.Solver.CLP_LINEAR_PROGRAMMING)

# add variables
x = dict()
y = dict()
for i in range(num_s):
    for j in range(num_d):
        x[i, j] = solver.NumVar(0, solver.infinity(), 'x[%i,%i]' % (i, j))
        y[i, j] = solver.IntVar(0, 1, 'y[%i,%i]' % (i, j))

    # add objective
z = solver.Sum([
    solver.Sum([
        c[i, j] * x[i, j] + f[i, j] * y[i, j]
        for i in range(num_s)
    ]) for j in range(num_d)
])
objective = solver.Minimize(z)

# add constraints
st_s = dict()
for i in range(num_s):
    st_s[i] = solver.Add(solver.Sum([x[i, j] for j in range(num_d)]) <= supply[i])
st_d = dict()
for j in range(num_d):
    st_d[i] = solver.Add(solver.Sum([x[i, j] for i in range(num_s)]) >= demand[j])
st_f = dict()
for i in range(num_s):
    for j in range(num_d):
        st_f[i, j] = solver.Add(x[i, j] <= M[i, j] * y[i, j])

# optimize
solver.Solve()

print('z = ', solver.Objective().Value())
for i in range(num_s):
    for j in range(num_d):
        print("x%i%i  " % (i, j) + str(x[i, j].solution_value()))
        print("y%i%i  " % (i, j) + str(y[i, j].solution_value()))

'''


# ====================== benders decomposition ======================


def mp(Q, E, iter_i, parameter):
    # read parameters
    num_s = parameter["num_s"]
    num_d = parameter["num_d"]
    supply = parameter["supply"]
    demand = parameter["demand"]
    c = parameter["c"]
    f = parameter["f"]
    stop = False

    # master problem
    print(" === master problem ===")
    master = pywraplp.Solver("master%i" % iter_i, pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    y = dict()
    for i in range(num_s):
        for j in range(num_d):
            y[i, j] = master.IntVar(0, 1, "y[%i,%i]" % (i, j))

    q = master.NumVar(0, master.infinity(), "q")

    # other constraints
    for i in range(num_s):
        master.Add(master.Sum([y[i, j] for j in range(num_d)]) >= 1)
    for j in range(num_d):
        master.Add(master.Sum([y[i, j] for i in range(num_s)]) >= 1)

    # general benders optimal cut
    for item in E.values():
        master.Add(
            master.Sum([-1 * supply[i] * item["u"][i] for i in range(num_s)]) +
            master.Sum([demand[j] * item["v"][j] for j in range(num_d)]) +
            master.Sum([
                -1 * M[i, j] * item["w"][i, j] * y[i, j]
                for i in range(num_s)
                for j in range(num_d)
            ]) <= q
        )

    # general benders feasible cuts
    # add extreme ray
    # or-tools does not support getRay() which exists in cplex
    # for item in Q.values():
    #     master.Add(
    #         master.Sum([-1 * supply[i] * item["u"][i] for i in range(num_s)]) +
    #         master.Sum([demand[j] * item["v"][j] for j in range(num_d)]) +
    #         master.Sum([
    #             -1 * M[i, j] * item["w"][i, j] * y[i, j]
    #             for i in range(num_s)
    #             for j in range(num_d)
    #         ]) <= 0
    #     )

    # combinatorial cuts
    for item in Q.values():
        master.Add(
            master.Sum([y[i, j] for (i, j) in item[0]]) +
            master.Sum([1 - y[i, j] for (i, j) in item[1]])
            >= 1
        )

    master.Minimize(master.Sum([
        f[i, j] * y[i, j]
        for i in range(num_s)
        for j in range(num_d)
    ]) + q)

    master_status = master.Solve()

    # if optimal or feasible
    bar_y = dict()
    if master_status == 0:
        for i in range(num_s):
            for j in range(num_d):
                bar_y[i, j] = 1 if y[i, j].solution_value() > 0.1 else 0
    else:
        print("There is no feasible solution in primal problem")
        stop = True

    return master, bar_y, stop


def sp(Q, E, bar_y, iter_i, parameter):
    # read parameters
    num_s = parameter["num_s"]
    num_d = parameter["num_d"]
    supply = parameter["supply"]
    demand = parameter["demand"]
    c = parameter["c"]
    f = parameter["f"]
    M = parameter["M"]
    stop = False

    # slave sub-problem
    print(" === slave sub-problem ===")
    slave = pywraplp.Solver("slave%i" % iter_i, pywraplp.Solver.CLP_LINEAR_PROGRAMMING)

    x = dict()
    for i in range(num_s):
        for j in range(num_d):
            x[i, j] = slave.NumVar(0, M[i, j], "x[%i,%i]" % (i, j))

    con_u = dict()
    for i in range(num_s):
        con_u[i] = slave.Add(slave.Sum([
            -1 * x[i, j] for j in range(num_d)
        ]) >= -1 * supply[i])

    con_v = dict()
    for j in range(num_d):
        con_v[j] = slave.Add(slave.Sum([
            x[i, j] for i in range(num_s)
        ]) >= demand[j])

    con_w = dict()
    for i in range(num_s):
        for j in range(num_d):
            con_w[i, j] = slave.Add(
                -1 * x[i, j] + M[i, j] * bar_y[i, j] >= 0
            )

    slave.Minimize(slave.Sum([
        c[i, j] * x[i, j]
        for i in range(num_s)
        for j in range(num_d)
    ]))

    slave_status = slave.Solve()

    if slave_status == slave.OPTIMAL:
        item = dict()
        item["u"] = {k: u.dual_value() for k, u in con_u.items()}
        item["v"] = {k: v.dual_value() for k, v in con_v.items()}
        item["w"] = {k: w.dual_value() for k, w in con_w.items()}
        E[iter_i] = item
    elif slave_status == slave.INFEASIBLE:
        # general benders feasible cuts should have been added
        # or-tools does not support getRay() which exists in cplex
        # so we add combinatorial cuts instead

        # combinatorial cuts
        item = defaultdict(list)
        for i in range(num_s):
            for j in range(num_d):
                if bar_y[i, j] > 0:
                    item[1].append((i, j))
                else:
                    item[0].append((i, j))
        Q[iter_i] = item
    else:
        print("wrong slave sub-problem status  " + str(slave_status))
        stop = True

    return slave, stop


Q_set = dict()
E_set = dict()

LB = -1 * 1e10
UB = 1e10

for iter_i in range(1000):

    if np.abs(UB - LB) < 0.01:
        print("Optimal")
        # break

    print("=" * 100)
    print("iteration at " + str(iter_i))

    slave, stop = sp(Q_set, E_set, bar_y, iter_i, params)

    print("Q  " + str(len(Q_set.keys())))
    print("E  " + str(len(E_set.keys())))

    if stop:
        print("Wong slave problem")
        break

    item = E_set.get(iter_i, False)
    if item:
        print("slave objective value")
        print(slave.Objective().Value())

        dual_optimal = sum(
            [-1 * supply[i] * item["u"][i] for i in range(num_s)]
        ) + sum(
            [demand[j] * item["v"][j] for j in range(num_d)]
        ) + sum(
            [-1 * M[i, j] * bar_y[i, j] * item["w"][i, j]
             for i in range(num_s)
             for j in range(num_d)]
        )

        print("slave dual objective value")
        print(dual_optimal)

        UB = min(
            UB, dual_optimal + sum(
                [bar_y[i, j] * f[i, j]
                 for i in range(num_s)
                 for j in range(num_d)]
            )
        )

    master, bar_y, stop = mp(Q_set, E_set, iter_i, params)

    print("bar_y")
    print(bar_y)

    print("master objective value")
    print(master.Objective().Value())

    if stop:
        print("wrong master problem")
        break

    LB = master.Objective().Value()

    print("UB " + str(UB))
    print("LB " + str(LB))
