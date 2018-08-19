from typing import *

from vrp_reader import read_data, get_node_info
from vrp_structure import SeqInfo
from vrp_util import generate_seq_info
from vrp_check import check_merge_seqs_available
from vrp_constant import *

data_set_num = 5
select_pair_num = None

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

seq_candidate = {*node_id_d, *node_id_p}    # type: Set[tuple]

# init route list
route_dict = {  # type: dict[tuple, SeqInfo]
    seq: SeqInfo(
        2, volume[seq], weight[seq], ds[(0,), seq] + ds[seq, (0,)], SERVE_TIME,
        first[seq], last[seq], first[seq] + SERVE_TIME, last[seq] + SERVE_TIME,
        0, 0, (ds[(0,), seq] + ds[seq, (0,)]) * TRANS_COST_2 + FIXED_COST_2 if (ds[(0,), seq] + ds[
            seq, (0,)]) <= DISTANCE_2 else M
    )
    for seq in seq_candidate
}

route_dict.update({
    seq: SeqInfo(
        2, 0, 0, ds[(0,), seq] + ds[seq, (0,)], SERVE_TIME,
        first[seq], last[seq], first[seq] + SERVE_TIME, last[seq] + SERVE_TIME,
        0, 1, (ds[(0,), seq] + ds[seq, (0,)]) * TRANS_COST_2 + FIXED_COST_2 + CHARGE_COST if (ds[(0,), seq] + ds[
            seq, (0,)]) <= DISTANCE_2 * 2 else M
    )
    for seq in node_id_c
})

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
                old_cost = route_dict[seq1].cost + route_dict[seq2].cost
                new_info = generate_seq_info(
                    seq1 + seq2, ds, tm, volume, weight,
                    first, last, node_type_judgement,
                    vehicle_type=2
                )
                if new_info is not None:
                    saving_value_pair_candidate[(seq1, seq2)] = (new_info, old_cost - new_info.cost)
    for seq2 in node_id_c:
        if ds[seq1, seq2] < 50000:
            is_available, err = check_merge_seqs_available(
                seq1, seq2, route_dict[seq1],
                route_dict[seq2],
                ds, tm
            )
            if is_available:
                old_cost = route_dict[seq1].cost + route_dict[seq2].cost
                new_info = generate_seq_info(
                    seq1 + seq2, ds, tm, volume, weight,
                    first, last, node_type_judgement,
                    vehicle_type=2
                )
                if new_info is not None:
                    saving_value_pair_candidate[(seq1, seq2)] = (new_info, old_cost - new_info.cost)

while True:

    print("*" * 30)
    print("saving value pair number: " + str(len(saving_value_pair_candidate.keys())))
    print("route number in the beginning: " + str(len(route_dict.keys())))
    print("candidate number in the beginning: " + str(len(seq_candidate)))

    # init saving value rank list
    saving_value_rank_list = []
    for (seq1, seq2), (new_info, saving_value) in saving_value_pair_candidate.items():
        if saving_value > 0:
            saving_value_rank_list.append((seq1, seq2, seq1 + seq2, new_info, saving_value))
    del saving_value_pair_candidate
    saving_value_rank_list.sort(key=lambda x: x[-1], reverse=True)

    # merge saving value pair
    merge_route_number = 0
    pop_route_set = set()
    for seq1, seq2, new_seq, new_info, saving_value in saving_value_rank_list[:select_pair_num]:
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

    del saving_value_rank_list
    print("merge route number: " + str(merge_route_number))
    print("pop route number: " + str(len(pop_route_set)))
    print("left seq_candidate: " + str(len(seq_candidate)))
    if merge_route_number == 0:
        break

    # construct new saving value pair
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
                    old_cost = route_dict[seq1].cost + route_dict[seq2].cost
                    new_info = generate_seq_info(
                        seq1 + seq2, ds, tm, volume, weight,
                        first, last, node_type_judgement,
                        vehicle_type=2
                    )
                    if new_info is not None:
                        saving_value_pair_candidate[(seq1, seq2)] = (new_info, old_cost - new_info.cost)
        for seq2 in node_id_c:
            if seq1[-1:] not in node_id_c and ds[seq1, seq2] < 50000:
                is_available, err = check_merge_seqs_available(
                    seq1, seq2, route_dict[seq1],
                    route_dict[seq2],
                    ds, tm
                )
                if is_available:
                    old_cost = route_dict[seq1].cost + route_dict[seq2].cost
                    new_info = generate_seq_info(
                        seq1 + seq2, ds, tm, volume, weight,
                        first, last, node_type_judgement,
                        vehicle_type=2
                    )
                    if new_info is not None:
                        saving_value_pair_candidate[(seq1, seq2)] = (new_info, old_cost - new_info.cost)

    print("route number in the end: " + str(len(route_dict.keys())))
    print("candidate number in the end: " + str(len(seq_candidate)))

print("~" * 30)
for cid in node_id_c:
    route_dict.pop(cid, None)
print("final route number: " + str(len(route_dict.keys())))

# for k, v in route_dict.items():
#     print("-" * 30)
#     print(k)
#     print(v)
#     print(generate_seq_info(k, ds, tm, volume, weight, first, last, node_type_judgement))
