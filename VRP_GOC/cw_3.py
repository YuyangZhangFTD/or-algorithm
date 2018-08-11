import pandas as pd

import vrp_util as util
from vrp_structure import SeqInfo, SeqDict


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

route_dict = {
    seq: SeqInfo(
        2,
        volume[seq],
        weight[seq],
        ds[(0,), seq] + ds[seq, (0,)],
        tm[(0,), seq] + 30 + tm[seq, (0,)],
        30, first[seq], last[seq], first[seq] + 30, last[seq] + 30,
        0, 0,
        ds[(0,), seq] * 2 * 14 / 1000 + 300 + 0 + 0  # dis + fixed + charge + wait
        if ds[(0,), seq] * 2 <= util.DISTANCE_2
        else util.M
    )
    for seq in seq_candidate  # seq == nid here
}

charge_seq_candidate = set([(x, ) for x in range(1001, 1101)])

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
    seq: SeqInfo(
        2,  0, 0,
        ds[(0,), seq] + ds[seq, (0,)],
        tm[(0,), seq] + 30 + tm[seq, (0,)],
        30, 0, 960, 30, 990,
        0, 1,
        ds[(0,), seq] * 2 * 14 / 1000 + 300 + 50 + 0  # dis + fixed + charge + wait
        if ds[(0,), seq] * 2 <= util.DISTANCE_2
        else util.M
    )
    for seq in charge_seq_candidate
})

