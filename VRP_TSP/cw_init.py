import pandas as pd

import util

node = pd.read_csv("input/node.csv")
# node = node.sample(n=100, random_state=0)
node_ids = node["ID"].values.tolist()

weight = pd.Series(node["weight"].values, index=node["ID"].values).to_dict()
volume = pd.Series(node["volume"].values, index=node["ID"].values).to_dict()
first = pd.Series(node["first"].values, index=node["ID"].values).to_dict()
last = pd.Series(node["last"].values, index=node["ID"].values).to_dict()

dt = pd.read_csv("input/input_distance-time.txt")
from_to_node = list(zip(dt["from_node"].values, dt["to_node"].values))
ds = pd.Series(dt["distance"].values, index=from_to_node).to_dict()
tm = pd.Series(dt["spend_tm"].values, index=from_to_node).to_dict()
del dt, from_to_node

# init route list
# TODO: add charge node pair
route_dict = {
    # {
    #   route_sequence:
    #       [ vehicle_type, weight, volume, distance, time,
    #           (es, ls, ef, lf, wait), cost
    #       ]
    # }
    (0, nid, 0): [
            2,  # default vehicle type 2
            weight[nid], volume[nid],
            ds[0, nid] + ds[nid, 0],
            tm[0, nid] + tm[nid, 0],
            (first[nid], last[nid], first[nid] + 30, last[nid] + 30, 0),
            ds[0, nid] * 2 * 14 + 300
    ]
    for nid in node_ids  # seq == nid here
}

# saving value pair candidate
saving_value_pair_candidate = set()
for nid1 in node_ids:
    for nid2 in node_ids:
        if nid1 == nid2:
            continue
        if (first[nid1], last[nid1]) <= (first[nid2], last[nid2]):
            if first[nid1] + 30 + tm[(nid1, nid2)] <= last[nid2]:
                saving_value_pair_candidate.add((nid1, nid2))

seq_candidate = set(node_ids)

# cw main
while True:

    # init saving value list
    saving_value_rank_list = []

    # calculate saving value
    # nid1 and nid2 can be sequence, such as (1,2,3)
    for seq1, seq2 in saving_value_pair_candidate.keys():

        new_route_time_info = util.arrange_time(
            first[seq1], last[seq1],
            first[seq2], last[seq2],
            tm[seq1, seq2]
        )

        wait = new_route_time_info[-1]

        seq1_tuple = seq1 if isinstance(seq1, tuple) else tuple([seq1])
        seq2_tuple = seq1 if isinstance(seq2, tuple) else tuple([seq2])

        new_cost, ds_len = util.calculate_sequence_cost(seq1_tuple + seq2_tuple, wait, 2, ds)
        saving_value = route_dict[tuple(util.seq2route(seq1_tuple))][-1] + \
                       route_dict[tuple(util.seq2route(seq2_tuple))][-1] - new_cost

        # [((seq1, seq2), saving_Value), ...]
        saving_value_rank_list.append((seq1_tuple + seq2_tuple, new_route_time_info, ds_len, new_cost, saving_value))

    saving_value_rank_list.sort(key=lambda x: x[-1], reverse=True)

    seq_i = None
    seq_j = None
    new_seq = None

    # find optimal sequence pair
    # attention: search top 200 for the optimal saving pair
    for (seq1, seq2), new_route_time_info, ds_len, new_cost, saving_value in saving_value_rank_list[:200]:
        # new sequence
        new_seq = seq1 + seq2

        # calculate total weight and volume
        w = 0
        v = 0
        for nid in new_seq:
            w += weight[nid]
            v += volume[nid]

        # check available
        if w > 2.5 or v > 16 or ds_len > 120000:
            continue
        else:
            seq_i = seq1
            seq_j = seq2
            # merge 2 sequences
            # vehicle_type, weight, volume, distance, time, (es, ls, ef, lf, wait), cost
            time_len = new_route_time_info[0] - new_route_time_info[2]
            route_dict[util.seq2route(new_seq)] = [2, w, v, ds_len, time_len, new_route_time_info.copy(), new_cost]
            break
    else:
        # the optimal value can not be found in top 200 sequence pairs
        break

    # update values
    # distance, time and saving_value_dict
    # del (i*, k), (k, j*) for any k
    # add ((i*,j*), k), (k, (i*,j*)) for any k
    # route: delete two old routes, and add new one
    # first, last
    route_dict.pop(util.seq2route(seq_i))
    route_dict.pop(util.seq2route(seq_j))
    for seq1 in seq_candidate:
        ds[new_seq, seq1] = ds[new_seq[-1], seq1]
        ds[seq1, new_seq] = ds[seq1, new_seq[0]]
        tm[new_seq, seq1] = tm[new_seq[-1], seq1]
        tm[seq1, new_seq] = tm[seq1, new_seq[0]]



        for seq2 in seq_candidate:
            if seq1 == seq2:
                continue
            else:
                if seq1 == seq_i:
                    ds.pop(seq1, seq2)
                    tm.pop(seq1, seq2)
                if seq2 == seq_j:
                    ds.pop(seq1, seq2)
                    tm.pop(seq1, seq2)


