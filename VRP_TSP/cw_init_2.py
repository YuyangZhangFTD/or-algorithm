import pandas as pd
import random
import copy

import util
from util import SeqDict


# ATTENTION
saving_value_threshold = 10

node = pd.read_csv("input_A/node.csv")
seq_candidate = {(x,) for x in node["ID"].values.tolist()}

weight = {
    (k,): v
    for k, v in pd.Series(node["weight"].values, index=node["ID"].values).items()
}
volume = {
    (k,): v
    for k, v in pd.Series(node["volume"].values, index=node["ID"].values).items()
}
first = {
    (k,): v
    for k, v in pd.Series(node["first"].values, index=node["ID"].values).items()
}
last = {
    (k,): v
    for k, v in pd.Series(node["last"].values, index=node["ID"].values).items()
}

dt = pd.read_csv("input_A/input_distance-time.txt")
from_to_node = list(zip(dt["from_node"].values, dt["to_node"].values))
ds = SeqDict({
    ((k1,), (k2,)): v
    for (k1, k2), v in pd.Series(dt["distance"].values, index=from_to_node).items()
})
tm = SeqDict({
    ((k1,), (k2,)): v
    for (k1, k2), v in pd.Series(dt["spend_tm"].values, index=from_to_node).items()
})
del dt, from_to_node

# init route list
route_dict = {
    # seq: [...]
    #   0 vehicle_type
    #   1 total_weight
    #   2 total_volume
    #   3 total_distance
    #   4 total_time
    #   5 time_info :       0       1   2   3   4   5
    #                   [time_len, es, ls, ef, lf, wait]
    #   6 charge_cnt
    #   7 cost
    seq: [
        2,  # default vehicle type 2
        weight[seq],
        volume[seq],
        ds[(0,), seq] + ds[seq, (0,)],
        tm[(0,), seq] + 30 + tm[seq, (0,)],
        (30, first[seq], last[seq], first[seq] + 30, last[seq] + 30, 0),
        0,
        # TODO, check whether available, if not, cost = util.M
        ds[(0,), seq] * 2 * 14 / 1000 + 300 + 0 + 0  # dis + fixed + charge + wait
        if ds[(0,), seq] * 2 <= util.DISTANCE_2
        else util.M
    ]
    for seq in seq_candidate  # seq == nid here
}

# add charge node
charge_seq_candidate = set([(x, ) for x in range(1001, 1101)])

# add charge seq in route_dict
route_dict.update({
    # seq: route_info[...]
    #   0 vehicle_type
    #   1 total_weight
    #   2 total_volume
    #   3 total_distance
    #   4 total_time
    #   5 time_info :       0       1   2   3   4   5
    #                   [time_len, es, ls, ef, lf, wait]
    #   6 charge_cnt
    #   7 cost
    seq: [
        2,  # default vehicle type 2
        0,
        0,
        ds[(0,), seq] + ds[seq, (0,)],  # 0 -> c -> n -> 0
        tm[(0,), seq] + 30 + tm[seq, (0,)],
        (
            30,
            0,
            960,
            30,
            990,
            0
        ),
        1,
        # dis + fixed + charge + wait
        # (ds[(0,), seq] + ds[seq, (0,)]) * 14 / 1000 + 300 + 50 + 0
        50  # extra charge cost
    ]
    for seq in charge_seq_candidate
})
seq_candidate.update(charge_seq_candidate)

route_dict_copy = copy.deepcopy(route_dict)

# init saving value pair
saving_value_pair_candidate = dict()
for seq1 in seq_candidate:
    for seq2 in seq_candidate:
        if seq1 == seq2:
            continue
        if seq1 in charge_seq_candidate or seq2 in charge_seq_candidate:
            saving_value_pair_candidate[(seq1, seq2)] = None
            continue

        if (first[seq1], last[seq1]) <= (first[seq2], last[seq2]):
            if util.check_merge_available(
                seq1, seq2,
                route_dict[seq1],
                route_dict[seq2],
                ds, tm
            ):
                saving_value_pair_candidate[(seq1, seq2)] = None

while True:

    print("*" * 100)

    pop_list = []

    # calculate saving value
    # nid1 and nid2 can be sequence, such as (1,2,3)
    for seq1, seq2 in saving_value_pair_candidate.keys():

        # TODO: useful?
        if seq1 not in seq_candidate or seq2 not in seq_candidate:
            continue

        if saving_value_pair_candidate[seq1, seq2] is not None:
            continue

        if not util.check_merge_available(
            seq1, seq2, route_dict[seq1], route_dict[seq2], ds, tm
        ):
            pop_list.append((seq1, seq2))
            continue

        new_route_time_info = util.generate_time_info(
            seq1, seq2,
            route_dict[seq1][5],
            route_dict[seq2][5],
            tm
        )
        new_wait = new_route_time_info[-1]

        new_cost, total_ds, total_tm = util.calculate_route_cost(
            seq1 + seq2, route_dict[seq1][0],
            route_dict[seq1][5][-1] + route_dict[seq2][5][-1],
            route_dict[seq1][6] + route_dict[seq2][6],
            ds, tm
        )
        saving_value = route_dict[seq1][-1] + route_dict[seq2][-1] - new_cost

        # saving_value_rank_list.append((
        #     (seq1, seq2),
        #     seq1 + seq2,
        #     new_route_time_info,
        #     total_ds,
        #     total_tm,
        #     new_cost,
        #     saving_value
        # ))
        saving_value_pair_candidate[seq1, seq2] = (
            seq1 + seq2,
            new_route_time_info,
            total_ds,
            total_tm,
            new_cost,
            saving_value
        )

    for pop in pop_list:
        saving_value_pair_candidate.pop(pop, None)
    # print("delete infeasible pairs: " + str(len(pop_list)))

    saving_value_rank_list = sorted(
        [
            x
            for x in saving_value_pair_candidate.items()
            if x[1] is not None
        ],
        key=lambda x: (-x[1][-1], x[1][-2])  # (-saving_value, new_cost)
    )

    # ATTENTION
    # select_pair = random.randint(0, 5)
    select_pair = 0
    try:
        if saving_value_rank_list[select_pair][1][-1] <= saving_value_threshold:
            break
    except IndexError:
        print(saving_value_rank_list[:select_pair+1])
        break
    print("current pair")
    print(saving_value_rank_list[select_pair])

    seq1, seq2 = saving_value_rank_list[select_pair][0]
    new_seq, new_route_time_info, total_ds, total_tm, new_cost, saving_value = \
        saving_value_rank_list[select_pair][1]
    # seq: route_info[...]
    #   0 vehicle_type
    #   1 total_weight
    #   2 total_volume
    #   3 total_distance
    #   4 total_time
    #   5 time_info :       0       1   2   3   4   5
    #                   [time_len, es, ls, ef, lf, wait]
    #   6 charge_cnt
    #   7 cost
    vehicle_type = route_dict[seq1][0]
    total_weight = route_dict[seq1][1] + route_dict[seq2][1]
    total_volume = route_dict[seq1][2] + route_dict[seq2][2]
    charge_cnt = route_dict[seq1][6] + route_dict[seq2][6]

    if seq1 not in charge_seq_candidate:
        route_dict.pop(seq1)
    if seq2 not in charge_seq_candidate:
        route_dict.pop(seq2)
    route_dict[new_seq] = [
        vehicle_type,
        total_weight,
        total_volume,
        total_ds,
        total_tm,
        new_route_time_info,
        charge_cnt,
        new_cost
    ]

    # ------------------------------- update values -------------------------------
    if seq1 not in charge_seq_candidate:
        seq_candidate.remove(seq1)
    if seq2 not in charge_seq_candidate:
        seq_candidate.remove(seq2)
    seq_candidate.add(new_seq)

    saving_value_pair_candidate.pop((seq1, seq2), None)
    saving_value_pair_candidate.pop((seq2, seq1), None)

    first.pop(seq1, None)
    first.pop(seq2, None)
    first[new_seq] = new_route_time_info[1]

    last.pop(seq1, None)
    last.pop(seq2, None)
    last[new_seq] = new_route_time_info[2]

    weight.pop(seq1, None)
    weight.pop(seq2, None)
    weight[new_seq] = total_weight

    volume.pop(seq1, None)
    volume.pop(seq2, None)
    volume[new_seq] = total_volume

    for seq_k in seq_candidate:

        if seq_k == new_seq or seq_k == seq1 or seq_k == seq2:
            continue

        if seq1 not in charge_seq_candidate:
            saving_value_pair_candidate.pop((seq1, seq_k), None)
            saving_value_pair_candidate.pop((seq_k, seq1), None)  # (seq_k, seq1) => (seq_k, new_seq)
        if seq2 not in charge_seq_candidate:
            saving_value_pair_candidate.pop((seq_k, seq2), None)
            saving_value_pair_candidate.pop((seq2, seq_k), None)  # (seq2, seq_k) => (new_seq, seq_k)

        es = new_route_time_info[1]
        ls = new_route_time_info[2]
        ef = new_route_time_info[3]

        if seq_k not in charge_seq_candidate:
            if (es, ls) <= (first[seq_k], last[seq_k]):
                # ef1 + t12 <= ls2
                if ef + tm[new_seq, seq_k] <= last[seq_k]:
                    saving_value_pair_candidate[(new_seq, seq_k)] = None
            else:
                # ef of seq_k
                if first[seq_k] + route_dict[seq_k][5][0] + tm[seq_k, new_seq] <= ls:
                    saving_value_pair_candidate[(seq_k, new_seq)] = None

    print("new route: ")
    print(util.seq2route(new_seq))
    print("vehicle_type, total_weight, total_volume, total_ds, "
          "total_tm, (time_len, es, ls, ef, lf, wait), charge_cnt, cost")
    print(route_dict[new_seq])
    print("now vehicle numbers: " + str(len(route_dict.keys())))

# delete
final_route_dict = dict()
for seq, info in route_dict.items():
    if len(seq) == 1 and seq[0] > 1000:
        continue
    k, v = util.delete_charge_end(seq, info, ds, tm)
    final_route_dict[k] = v
del route_dict

print("finial vehicle numbers: " + str(len(final_route_dict.keys())))

cost = 0
print("=" * 45 + "result" + "=" * 45)
for seq, v in final_route_dict.items():
    print(util.seq2route(seq))
    cost += v[-1]

print("Final cost: " + str(cost))

print("saving result")
util.save_result(final_route_dict, tm)
