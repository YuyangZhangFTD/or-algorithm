from typing import *

from vrp_reader import read_data, get_node_info
from vrp_structure import SeqInfo
from vrp_util import generate_seq_info
from vrp_check import check_merge_seqs_available
from vrp_constant import *

data_set_num = 5
merge_seq_each_time = 50

ds, tm, delivery, pickup, charge, node_type_judgement = read_data(data_set_num)
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

seq_candidate = {*node_id_d, *node_id_p}  # type: Set[tuple]

# init route list
route_dict = {  # type: dict[tuple, SeqInfo]
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
    for seq in seq_candidate
}

# init saving value pair
saving_value_pair_candidate = dict()
for seq1 in seq_candidate:
    for seq2 in seq_candidate:
        if seq1 == seq2:
            continue
        if (first[seq1], last[seq1]) <= (first[seq2], last[seq2]):
            is_available, err = check_merge_seqs_available(
                seq1, seq2, route_dict[seq1],
                route_dict[seq2],
                ds, tm
            )
            if is_available:
                new_seq = seq1 + seq2
            elif err == 4:      # add change node and construct a feasible sequence
                charge_nodes = [(cid, ds[seq1, cid]+ds[cid, seq2]) for cid in node_id_c]
                charge_nodes.sort(key=lambda x: x[-1])
                new_seq = seq1 + charge_nodes[0][0] + seq2
                del charge_nodes
            else:
                continue

            old_cost = route_dict[seq1].cost + route_dict[seq2].cost
            new_info = generate_seq_info(
                new_seq, ds, tm, volume, weight,
                first, last, node_type_judgement,
                vehicle_type=2
            )
            if new_info is not None:
                saving_value_pair_candidate[(seq1, seq2)] = (new_seq, new_info, old_cost - new_info.cost)

print(len(saving_value_pair_candidate))

while True:

    print("*" * 30)
    print("saving value pair number: " + str(len(saving_value_pair_candidate.keys())))
    print("route number in the beginning: " + str(len(route_dict.keys())))
    print("candidate number in the beginning: " + str(len(seq_candidate)))

    # init saving value rank list
    saving_value_rank_list = []
    for (seq1, seq2), (new_seq, new_info, saving_value) in saving_value_pair_candidate.items():
        if saving_value > 0:
            saving_value_rank_list.append((seq1, seq2, new_seq, new_info, saving_value))
    del saving_value_pair_candidate
    saving_value_rank_list.sort(key=lambda x: x[-1], reverse=True)

    # merge saving value pair
    merge_route_number = 0
    pop_route_set = set()
    for seq1, seq2, new_seq, new_info, saving_value in saving_value_rank_list:
        if seq1 not in pop_route_set and seq2 not in pop_route_set and new_info is not None:

            if seq1 not in node_id_c:
                seq_candidate.remove(seq1)
                route_dict.pop(seq1)
                pop_route_set.add(seq1)
            if seq2 not in node_id_c:
                seq_candidate.remove(seq2)
                route_dict.pop(seq2)
                pop_route_set.add(seq2)

            route_dict[new_seq] = new_info
            seq_candidate.add(new_seq)
            first[new_seq] = new_info.es
            last[new_seq] = new_info.ls
            weight[new_seq] = new_info.weight
            volume[new_seq] = new_info.volume
            merge_route_number += 1

            if merge_route_number > merge_seq_each_time:
                break

    del saving_value_rank_list
    print("merge route number: " + str(merge_route_number))
    print("pop route number: " + str(len(pop_route_set)))
    print("left seq_candidate: " + str(len(seq_candidate)))
    if merge_route_number == 0:
        break

    # construct new saving value pair
    # init saving value pair
    saving_value_pair_candidate = dict()
    for seq1 in seq_candidate:
        for seq2 in seq_candidate:
            if seq1 == seq2:
                continue
            if (first[seq1], last[seq1]) <= (first[seq2], last[seq2]):
                is_available, err = check_merge_seqs_available(
                    seq1, seq2, route_dict[seq1],
                    route_dict[seq2],
                    ds, tm
                )
                if is_available:
                    new_seq = seq1 + seq2
                elif err == 4:  # add change node and construct a feasible sequence
                    charge_nodes = [(cid, ds[seq1, cid] + ds[cid, seq2]) for cid in node_id_c]
                    charge_nodes.sort(key=lambda x: x[-1])
                    new_seq = seq1 + charge_nodes[0][0] + seq2
                    del charge_nodes
                else:
                    continue

                old_cost = route_dict[seq1].cost + route_dict[seq2].cost
                new_info = generate_seq_info(
                    new_seq, ds, tm, volume, weight,
                    first, last, node_type_judgement,
                    vehicle_type=2
                )
                if new_info is not None:
                    saving_value_pair_candidate[(seq1, seq2)] = (new_seq, new_info, old_cost - new_info.cost)

    print("route number in the end: " + str(len(route_dict.keys())))
    print("candidate number in the end: " + str(len(seq_candidate)))

cost = 0
for k, v in route_dict.items():
    print("-" * 30)
    print(k)
    print(v)
    v_ = generate_seq_info(k, ds, tm, volume, weight, first, last, node_type_judgement)
    print(v_)
    cost += v_.cost

print("final cost: " + str(cost))
