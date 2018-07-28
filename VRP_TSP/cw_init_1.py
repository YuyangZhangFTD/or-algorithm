import pandas as pd

import util

node = pd.read_csv("input/node.csv")
# node = node.sample(n=100, random_state=0)
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

dt = pd.read_csv("input/input_distance-time.txt")
from_to_node = list(zip(dt["from_node"].values, dt["to_node"].values))
ds = {
    ((k1,), (k2,)): v
    for (k1, k2), v in pd.Series(dt["distance"].values, index=from_to_node).items()
}

tm = {
    ((k1,), (k2,)): v
    for (k1, k2), v in pd.Series(dt["spend_tm"].values, index=from_to_node).items()
}
del dt, from_to_node

# init route list
# TODO: add charge node pair
route_dict = {
    # {
    #   route_sequence:
    #       [ vehicle_type, weight, volume, distance, time,
    #           (es, ls, ef, lf, wait), charge_cnt, cost
    #       ]
    # }
    seq: [
        2,  # default vehicle type 2
        weight[seq], volume[seq],
        ds[(0,), seq] + ds[seq, (0,)],
        tm[(0,), seq] + 30 + tm[seq, (0,)],
        (first[seq], last[seq], first[seq] + 30, last[seq] + 30, 0),
        0, ds[(0,), seq] * 2 * 14 + 300
    ]
    for seq in seq_candidate  # seq == nid here
}

# saving value pair candidate
saving_value_pair_candidate = set()
for seq1 in seq_candidate:
    for seq2 in seq_candidate:
        if seq1 == seq2:
            continue
        if (first[seq1], last[seq1]) <= (first[seq2], last[seq2]):
            if first[seq1] + 30 + tm[(seq1, seq2)] <= last[seq2]:
                saving_value_pair_candidate.add((seq1, seq2))

# cw main
while True:

    # init saving value list
    saving_value_rank_list = []

    print("*" * 100)

    # calculate saving value
    # nid1 and nid2 can be sequence, such as (1,2,3)
    for seq1, seq2 in saving_value_pair_candidate:

        new_route_time_info = util.arrange_time(
            first[seq1], last[seq1],
            first[seq2], last[seq2],
            tm[seq1, seq2]
        )

        wait = new_route_time_info[-1]

        # ds_len contains ds[0,seq[0]] and ds[seq[-1],0]
        new_cost, ds_len = util.calculate_sequence_cost(seq1 + seq2, wait, 2, ds)
        saving_value = route_dict[seq1][-1] + route_dict[seq2][-1] - new_cost

        if ds_len > 120000:  # without consider charging
            continue

        # [((seq1, seq2), new_seq, (es, ls, ef, lf, wait), ds_len, cost, saving_Value), ...]
        saving_value_rank_list.append((
            (seq1, seq2),
            seq1 + seq2,
            new_route_time_info,  # should we add .copy()?
            ds_len,
            new_cost,
            saving_value
        ))

    saving_value_rank_list.sort(key=lambda x: x[-1], reverse=True)

    # find optimal sequence pair
    # attention: search top 200 for the optimal saving pair
    for (seq1, seq2), new_seq, new_route_time_info, ds_len, new_cost, saving_value \
            in saving_value_rank_list:

        # calculate total weight and volume
        w = weight[seq1] + weight[seq2]
        v = volume[seq1] + volume[seq2]

        # check available
        if w > 2.5 or v > 16 or ds_len > 120000:
            continue
        else:
            # get charge node info
            charge_cnt = route_dict[seq1][6] + route_dict[seq2][6]

            # merge 2 sequences
            # vehicle_type, weight, volume, distance, time, (es, ls, ef, lf, wait), charge_cnt, cost
            time_len = new_route_time_info[2] - new_route_time_info[0]  # ef - es
            route_dict.pop(seq1)
            route_dict.pop(seq2)
            route_dict[new_seq] = [
                2, w, v, ds_len, time_len,
                new_route_time_info,
                charge_cnt, new_cost
            ]

            # ------------------------------- update values -------------------------------
            # in seq_candidate, first, last, weight, volume
            # del seq1 and seq2
            # add new_seq
            seq_candidate.remove(seq1)
            seq_candidate.remove(seq2)
            seq_candidate.add(new_seq)

            first.pop(seq1)
            first.pop(seq2)
            first[new_seq] = new_route_time_info[0]  # early start

            last.pop(seq1)
            last.pop(seq2)
            last[new_seq] = new_route_time_info[1]  # late start

            weight.pop(seq1)
            weight.pop(seq2)
            weight[new_seq] = w

            volume.pop(seq1)
            volume.pop(seq2)
            volume[new_seq] = v

            # in saving_value_pair_candidate, ds, tm
            # del (seq1, seq_k), (seq_k, seq_2), (seq_k, seq1), (seq2, seq_k)
            # and add (new_seq, seq_k), (seq_k, new_seq) if available
            saving_value_pair_candidate.remove((seq1, seq2))
            if (seq2, seq1) in saving_value_pair_candidate:
                saving_value_pair_candidate.remove((seq2, seq1))

            ds[(new_seq, (0,))] = ds[(new_seq[-1:], (0,))]
            ds[((0,), new_seq)] = ds[((0,), new_seq[:1])]
            tm[(new_seq, (0,))] = tm[(new_seq[-1:], (0,))]
            tm[((0,), new_seq)] = tm[((0,), new_seq[:1])]

            for seq_k in seq_candidate:
                if seq_k == new_seq or seq_k == seq1 or seq_k == seq2:
                    continue

                ds[(new_seq, seq_k)] = ds[new_seq[-1:], seq_k[:1]]
                ds[(seq_k, new_seq)] = ds[seq_k[-1:], new_seq[:1]]
                # ds.pop((seq1, seq2))
                # ds.pop((seq1, seq_k))
                # ds.pop((seq_k, seq2))

                tm[(new_seq, seq_k)] = tm[new_seq[-1:], seq_k[:1]]
                tm[(seq_k, new_seq)] = tm[seq_k[-1:], new_seq[:1]]
                # tm.pop((seq1, seq2))
                # tm.pop((seq1, seq_k))
                # tm.pop((seq_k, seq2))

                # we add rules for generating saving_value_pair_candidate
                # key error is legal
                if (seq1, seq_k) in saving_value_pair_candidate:
                    saving_value_pair_candidate.remove((seq1, seq_k))
                if (seq_k, seq2) in saving_value_pair_candidate:
                    saving_value_pair_candidate.remove((seq_k, seq2))
                if (seq_k, seq1) in saving_value_pair_candidate:
                    saving_value_pair_candidate.remove((seq_k, seq1))  # (seq_k, seq1) => (seq_k, new_seq)
                if (seq2, seq_k) in saving_value_pair_candidate:
                    saving_value_pair_candidate.remove((seq2, seq_k))  # (seq2, seq_k) => (new_seq, seq_k)

                es = new_route_time_info[0]
                ls = new_route_time_info[1]
                ef = new_route_time_info[2]
                if (es, ls) <= (first[seq_k], last[seq_k]):
                    if ef + tm[new_seq, seq_k] <= last[seq_k]:  # early_finish_1 + road_time <= last_finish_2
                        saving_value_pair_candidate.add((new_seq, seq_k))
                else:
                    if first[seq_k] + 30 + tm[seq_k, new_seq] <= ls:
                        saving_value_pair_candidate.add((seq_k, new_seq))

            print("new route: ")
            print(util.seq2route(new_seq))
            print("vehicle_type, weight, volume, distance, time, (es, ls, ef, lf, wait), charge_cnt, cost")
            print([2, w, v, ds_len, time_len, new_route_time_info.copy(), charge_cnt, new_cost])
            break
    else:
        print("the optimal value can not be found in top 200 sequence pairs")
        break

# optimize with charge node
charge_nodes = {
    (nid,)
    for nid in range(1001, 1101)
}

pop_route = []
update_route = dict()

for seq, info in route_dict.items():
    if len(seq) > 1:
        continue

    # add charge node
    if info[3] > 120000:
        tmp_dis = 220000
        tmp_charge = -1
        for charge in charge_nodes:
            if ds[(0,), seq] + ds[seq, charge] + ds[charge, (0,)] < tmp_dis:
                # vehicle_type, weight, volume, distance, time, (es, ls, ef, lf, wait), charge_cnt, cost
                tmp_dis = ds[(0,), seq] + ds[seq, charge] + ds[charge, (0,)]
                tmp_charge = charge
        pop_route.append(seq)
        update_route[seq + tmp_charge] = [
            info[0], info[1], info[2],
            tmp_dis, info[4] - tm[seq, (0,)] + tm[seq, tmp_charge] + tm[tmp_charge, (0,)],
            info[5], 1, util.calculate_sequence_cost(seq, info[5][-1], 2, ds)[0]
        ]
        first[seq + tmp_charge] = info[5][0]
        tm[(0,), seq + tmp_charge] = tm[(0,), seq[:1]]
        tm[seq + tmp_charge, (0,)] = tm[seq[-1:], (0,)]

    # change vehicle type
    elif info[3] < 100000 and info[1] < 2 and info[2] < 12:
        update_route[seq] = [
            1, info[1], info[2], info[3], info[4],
            info[5], 0, util.calculate_sequence_cost(seq, info[5][-1], 1, ds)[0]
        ]

for seq in pop_route:
    route_dict.pop(seq)

route_dict.update(update_route)

cost = 0
print("=" * 45 + "result" + "=" * 45)
for seq, v in route_dict.items():
    print(util.seq2route(seq))
    c, d = util.calculate_sequence_cost(seq, 0, 2, ds)
    cost += c

print("Final cost: " + str(cost))

print("saving result")
util.save(route_dict, tm, first)
