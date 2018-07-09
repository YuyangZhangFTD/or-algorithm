import numpy as np
from gurobipy import *

example = 1
cuts_type = "general"
# cuts_type = "cb"

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
        [1, 0, 0],
        [0, 0, 1],
        [1, 0, 0],
        [0, 0, 1]
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
    ]).reshape(num_s, num_d)
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

"""
# ====================== solve problem directly ====================== 
mip = Model()
x = mip.addVars([i for i in range(num_s)], [j for j in range(num_d)], vtype=GRB.CONTINUOUS, name="x")
y = mip.addVars([i for i in range(num_s)], [j for j in range(num_d)], vtype=GRB.BINARY, name="y")
mip.setObjective(
    quicksum(
        quicksum(
            x[i,j] * c[i,j] + y[i,j] * f[i,j]
            for j in range(num_d)
        )
        for i in range(num_s)
    ), GRB.MINIMIZE
)
u = mip.addConstrs((
    quicksum(
        x[i,j] for j in range(num_d)
    ) <= supply[i]
    for i in range(num_s) 
))
v = mip.addConstrs((
    quicksum(
        x[i,j] for i in range(num_s)
    ) >= demand[j]
    for j in range(num_d)
))
w = mip.addConstrs((
    x[i,j] <= M[i,j] * y[i,j]
    for i in range(num_s)
    for j in range(num_d)
))

mip.optimize()
"""

# ====================== benders decomposition ======================
def mp(Q, E, iter_i, parameter, cuts_type):
    # read parameters
    num_s = parameter["num_s"]
    num_d = parameter["num_d"]
    supply = parameter["supply"]
    demand = parameter["demand"]
    c = parameter["c"]
    f = parameter["f"]
    stop = False

    # master problem
    print("=" * 20 + " master problem " + "=" * 20)
    master = Model("master")

    y = master.addVars(
        [i for i in range(num_s)],
        [j for j in range(num_d)],
        vtype=GRB.BINARY, name="y"
    )

    q = master.addVar(vtype=GRB.CONTINUOUS, name="q")

    master.addConstrs((
        quicksum(y[i,j] for i in range(num_s)) >= 1
        for j in range(num_d)
    ))

    master.addConstrs((
        quicksum(y[i,j] for j in range(num_d)) >= 1
        for i in range(num_s)
    ))

    if cuts_type == "general":
        # benders feasible cut
        for item in Q.values():
            master.addConstr(
                quicksum(-1 * supply[i] * item["u"][i] for i in range(num_s)) +
                quicksum(demand[j] * item["v"][j] for j in range(num_d)) +
                quicksum(-1 * M[i, j] * item["w"][i, j] * y[i, j] for i in range(num_s) for j in range(num_d))
                <= 0
            )
    elif cuts_type == "cb":
        # addConstraints do not support dict enumeration
        # benders feasible combinatorial cut
        for item in Q.values():
            master.addConstr(
                quicksum(y[i, j] for (i, j) in item[0]) +
                quicksum(1 - y[i, j] for (i, j) in item[1]) >= 1
            )
    else:
        print("no available cuts types")

    # benders optimality cut
    for item in E.values():
        master.addConstr(
            quicksum(-1 * supply[i] * item["u"][i] for i in range(num_s)) +
            quicksum(demand[j] * item["v"][j] for j in range(num_d)) +
            quicksum(-1 * M[i, j] * item["w"][i, j] * y[i, j] for i in range(num_s) for j in range(num_d))
            <= q
        )

    master.setObjective(quicksum(
        f[i, j] * y[i, j]
        for i in range(num_s)
        for j in range(num_d)
    ) + q, GRB.MINIMIZE)

    master.optimize()
    bar_y = dict()
    if master.status == GRB.OPTIMAL:
        for i in range(num_s):
            for j in range(num_d):
                bar_y[i, j] = 1 if y[i, j].x > 0.01 else 0
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

    # dual problem of slave problem
    print("=" * 20 + " slave problem with general feasible cuts " + "=" * 20)
    dual = Model("dual_slave")

    # get unboundedRay
    dual.Params.InfUnbdInfo = 1

    u = dual.addVars([i for i in range(num_s)], name="u")
    v = dual.addVars([j for j in range(num_d)], name="v")
    w = dual.addVars([i for i in range(num_s)], [j for j in range(num_d)], name="w")

    dual.setObjective(
        quicksum(-1 * supply[i] * u[i] for i in range(num_s)) +
        quicksum(demand[j] * v[j] for j in range(num_d)) +
        quicksum(
            -1 * M[i,j] * bar_y[i,j] * w[i,j]
            for i in range(num_s)
            for j in range(num_d)
        ), GRB.MAXIMIZE
    ) 

    dual.addConstrs((
        -1 * u[i] + v[j] - w[i,j] <= c[i,j]
        for i in range(num_s)
        for j in range(num_d)
    ))

    dual.optimize()

    if dual.status == GRB.UNBOUNDED:
        item = dict()
        item["u"] = {i:u[i].unbdRay for i in range(num_s)}
        item["v"] = {j:v[j].unbdRay for j in range(num_d)}
        item["w"] = {(i,j):w[i,j].unbdRay for i in range(num_s) for j in range(num_d)}
        Q[iter_i] = item
        print("Add feasible cut")
    elif dual.status == GRB.OPTIMAL:
        item = dict()
        item["u"] = {i:u[i].x for i in range(num_s)}
        item["v"] = {j:v[j].x for j in range(num_d)}
        item["w"] = {(i,j):w[i,j].x for i in range(num_s) for j in range(num_d)}
        E[iter_i] = item
        print("Add optimal cut")
    else:
        print("wrong slave sub-problem status  " + str(dual.status))
        stop = True

    return dual, stop


def sp_cb(Q, E, bar_y, iter_i, parameter):
    # read parameters
    num_s = parameter["num_s"]
    num_d = parameter["num_d"]
    supply = parameter["supply"]
    demand = parameter["demand"]
    c = parameter["c"]
    f = parameter["f"]
    M = parameter["M"]
    stop = False

    # slave problem
    print("=" * 20 + " slave problem with cb feasible cuts " + "=" * 20)
    slave = Model("slave")

    x = slave.addVars(
        [i for i in range(num_s)],
        [j for j in range(num_d)],
        vytpe=GRB.CONTINUOUS, name="x"
    )

    con_u = slave.addConstrs((
        quicksum(
            -1 * x[i, j] for j in range(num_d)
        ) >= -1 * supply[i]
        for i in range(num_s)
    ))

    con_v = slave.addConstrs((
        quicksum(
            x[i, j] for i in range(num_s)
        ) >= demand[j]
        for j in range(num_d)
    ))

    con_w = slave.addConstrs((
        -1 * x[i, j] + bar_y[i, j] * M[i, j] >= 0
        for i in range(num_s)
        for j in range(num_d)
    ))

    slave.setObjective(quicksum(
        c[i, j] * x[i, j]
        for i in range(num_s)
        for j in range(num_d)
    ), GRB.MINIMIZE)

    slave.optimize()

    if slave.status == GRB.INFEASIBLE:
        item = dict()
        item[0] = [
            k for k, v in bar_y.items() if v < 0.001
        ]
        item[1] = [
            k for k, v in bar_y.items() if v >= 0.001
        ]
        Q[iter_i] = item
        print("Add feasible cut")
    elif slave.status == GRB.OPTIMAL:
        item = dict()
        item["u"] = {k: v.pi for k, v in con_u.items()}
        item["v"] = {k: v.pi for k, v in con_v.items()}
        item["w"] = {k: v.pi for k, v in con_w.items()}
        E[iter_i] = item
        print("Add optimal cut")
    else:
        print("wrong slave sub-problem status  " + str(slave_status))
        stop = True

    return slave, stop


E_set = dict()
Q_set = dict()

LB = -1 * 1e10
UB = 1e10

warm_start = True
feasible_cnt = 0
optimal_cnt = 0

for iter_i in range(1000):

    if np.abs(UB - LB) < 0.01:
        print("Optimal")
        break

    print("=" * 100)
    print("iteration at " + str(iter_i))

    if cuts_type == "general":
        dual, stop = sp(Q_set, E_set, bar_y, iter_i, params)
        
    elif cuts_type == "cb":
        slave, stop = sp_cb(Q_set, E_set, bar_y, iter_i, params)

    else:
        print("no available cuts type")
        break

    print("Q  " + str(len(Q_set.keys())))
    print("E  " + str(len(E_set.keys())))

    if stop:
        print("Wong slave problem")
        break

    item = E_set.get(iter_i, False)
    if item:

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
    
    master, bar_y, stop = mp(Q_set, E_set, iter_i, params, cuts_type)

    print("bar_y")
    print(bar_y)

    print("master objective value")
    print(master.objVal)

    if stop:
        print("wrong master problem")
        break

    LB = master.objVal

    print("UB " + str(UB))
    print("LB " + str(LB))
