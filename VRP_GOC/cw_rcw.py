from vrp.io.reader import read_data, get_node_info
from vrp.io.result import save_result
from vrp.construction import saving_value_construct
from vrp.common.model import SeqInfo
from vrp.improvement import two_opt
from vrp.util.info import get_neighborhood_dict
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
# ntj = node_type_judgement
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

# ======================== init route list ==========================
init_route_dict = {
    seq: SeqInfo(
        2, volume[seq], weight[seq], ds[(0,), seq] + ds[seq, (0,)],
        tm[(0,), seq] + SERVE_TIME + tm[seq, (0,)],
        0 if first[seq] - tm[(0,), seq] < 0 else first[seq] - tm[(0,), seq],
        last[seq] - tm[(0,), seq],
        first[seq] + SERVE_TIME + tm[seq, (0,)],
        last[seq] + SERVE_TIME + tm[seq, (0,)],
        0, 0, (ds[(0,), seq] + ds[seq, (0,)]) * TRANS_COST_2 + FIXED_COST_2 if
        ds[(0,), seq] + ds[seq, (0,)] <= DISTANCE_2 else M
    )
    for seq in candidate_seqs
}

# ============================== vrp ================================
route_dict = saving_value_construct(
    candidate_seqs, init_route_dict, ds, tm, volume, weight,
    first, last, ntj, node_id_c,
    time_sorted_limit=time_sorted_limit,
    merge_seq_each_time=merge_seq_each_time
)
del candidate_seqs

is_charge = ntj[-1]
have_updated = False
neighborhood_dict = get_neighborhood_dict(
    route_dict, position, neighborhood_number=neighborhood_number
)

for _ in range(local_reconstruct_times):
    old_cost, new_cost = 0, 0
    if have_updated:
        neighborhood_dict = get_neighborhood_dict(
            route_dict, position, neighborhood_number=neighborhood_number
        )
        have_updated = False
    print("="*100)
    seq = choice(list(route_dict.keys()))
    old_cost += route_dict[seq].cost
    neighborhood = neighborhood_dict[seq]
    old_cost += sum([route_dict[x].cost for x in neighborhood])

    candidate_seqs = [
        (x,) for x in
        seq + reduce(lambda x, y: x + y, neighborhood)
        if not is_charge(x)
    ]
    local_route_dict = {
        seq: init_route_dict[seq]
        for seq in candidate_seqs
    }
    local_route_dict = saving_value_construct(
        candidate_seqs, local_route_dict,
        ds, tm, volume, weight, first, last,
        ntj, node_id_c,
        time_sorted_limit=time_sorted_limit,
        merge_seq_each_time=merge_seq_each_time
    )
    new_cost += sum([v.cost for v in local_route_dict.values()])
    if new_cost < old_cost:
        route_dict.pop(seq)
        print(seq)
        for seq_neighborhood in neighborhood:
            route_dict.pop(seq_neighborhood)
            print(seq_neighborhood)
        print("-" * 10)
        print("new routes: " + str(len(local_route_dict.keys())))
        route_dict.update(local_route_dict)
        have_updated = True


cost = 0
for k, v in route_dict.items():
    new_seq, new_info = two_opt(
        k, v, ds, tm, volume, weight, first, last, ntj,
        iter_num=15
    )
    cost += new_info.cost
    # print(new_seq)
    # print(new_info)

# ============================== save ===============================
print("final cost: " + str(cost))
save_result(route_dict, data_set_num)
