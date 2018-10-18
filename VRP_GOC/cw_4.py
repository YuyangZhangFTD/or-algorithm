from vrp.io.reader import read_data, get_node_info
from vrp.util.info import generate_seq_info
from vrp.io.result import save_result
from vrp.construction import merge_saving_value_pairs
from vrp.common.model import SeqInfo, Param
from vrp.common.constant import *

from copy import deepcopy


data_set_num = 5
merge_seq_each_time = 5
time_sorted_limit = False   # False for greedy matching

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

# init route list
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

route_dict = deepcopy(init_route_dict)
while True:
    route_dict, new_seq_count = merge_saving_value_pairs(
        candidate_seqs, route_dict, param , node_id_c,
        time_sorted_limit=time_sorted_limit,
        merge_seq_each_time=merge_seq_each_time
    )
    # update candidate seqs
    candidate_seqs = list(route_dict.keys())
    print("merge_seq_count: " + str(new_seq_count))
    if new_seq_count < 1:
        break

cost = 0
for k, v in route_dict.items():
    v_ = generate_seq_info(k, param)
    route_dict[k] = v_
    cost += v_.cost
    print(k)
    print(v_)

print("final cost: " + str(cost))
save_result(route_dict, data_set_num)
