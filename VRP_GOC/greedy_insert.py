from vrp.io.reader import read_data, get_node_info
from vrp.construction import saving_value_construct
from vrp.common.model import SeqInfo, Param
from vrp.util.neighborhhod import get_neighborhood_dict
from vrp.common.constant import *

from random import choice
from functools import reduce

# =========================== parameters ============================
data_set_num = 5
merge_seq_each_time = 300
time_sorted_limit = False  # False for greedy matching
local_reconstruct_times = 1000
neighborhood_number = 10

# =========================== read data =============================
# ntj: node_type_judgement
ds, tm, delivery, pickup, charge, position, ntj = read_data(data_set_num)
delivery = get_node_info(delivery)
pickup = get_node_info(pickup)
charge = get_node_info(charge, is_charge=True)
node_id_d, volume_d, weight_d, first_d, last_d = delivery
node_id_p, volume_p, weight_p, first_p, last_p = pickup
node_id_c, _, _, first_c, last_c = charge

volume = {**volume_d, **volume_p}
del volume_d, volume_p
weight = {**weight_d, **weight_p}
del weight_d, weight_p
first = {**first_d, **first_p, **first_c}
del first_d, first_p, first_c
last = {**last_d, **last_p, **last_c}
del last_d, last_p, last_c

first[(0,)] = 0
last[(0,)] = 960

candidate_seqs = {*node_id_d, *node_id_p}
param = Param(ds, tm, volume, weight, first, last, ntj, position)

# ======================== init route list ==========================
init_route_dict = dict()
for seq in candidate_seqs:
    # 0 if first[seq] - tm[(0,), seq] < 0 else first[seq] - tm[(0,), seq],
    # last[seq] - tm[(0,), seq],
    eps_list = [
        0,
        tm[(0,), seq],
        tm[(0,), seq] + SERVE_TIME + tm[seq, (0,)]
    ]
    lps_list = [
        last[seq] - tm[(0,), seq],
        last[seq],
        last[seq] + SERVE_TIME + tm[seq, (0,)]
    ]
    cost = (ds[(0,), seq] + ds[seq, (0,)]) * TRANS_COST_2 + FIXED_COST_2 if \
        ds[(0,), seq] + ds[seq, (0,)] <= DISTANCE_2 else M

    init_route_dict[seq] = SeqInfo(
        2, volume[seq], weight[seq], ds[(0,), seq] + ds[seq, (0,)],
        eps_list, lps_list,
        first[seq] + SERVE_TIME + tm[seq, (0,)],
        last[seq] + SERVE_TIME + tm[seq, (0,)],
        0, 0, cost
    )

# ============================== vrp ================================
route_dict = saving_value_construct(
    candidate_seqs, init_route_dict, param, node_id_c,
    time_sorted_limit=time_sorted_limit,
    merge_seq_each_time=merge_seq_each_time
)
del candidate_seqs

# ======================= greedy insert ==============================
neighborhood_dict = get_neighborhood_dict(
    route_dict, position, neighborhood_number=neighborhood_number
)

for _ in range(1):
    route_list = list(route_dict.keys())
    seed_route = choice(route_list)
    seed_neighborhood = neighborhood_dict.pop(seed_route)
    cost = 0
    for k in [seed_route, *seed_neighborhood]:
        cost += route_dict[k].cost
    print("old cost: " + str(cost))
    re_nodes = set(map(
        lambda x: (x,),
        reduce(lambda x, y: x + y, [seed_route, *seed_neighborhood])
    ))
    # re_route_dict = saving_value_construct(
    #     re_nodes, init_route_dict, param, node_id_c,
    #     time_sorted_limit=time_sorted_limit,
    #     merge_seq_each_time=merge_seq_each_time
    # )
    update = False
    re_route_dict = dict()
    while True:
        seed = re_nodes.pop()

        if not update:
            break

    cost = 0
    for k, v in re_route_dict.items():
        cost += v.cost
    print("new cost: " + str(cost))


"""
# ========================= evaluation ===============================
cost = 0
for k, v in route_dict.items():
    new_seq, new_info = two_opt(k, v, param, best_accept=True)
    cost += new_info.cost
print("final cost: " + str(cost))
"""
