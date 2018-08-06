import pandas as pd
from collections import namedtuple

TRANS_COST_1 = 12 / 1000
TRANS_COST_2 = 14 / 1000
FIXED_COST_1 = 200
FIXED_COST_2 = 300
WAIT_COST = 24 / 60
CHARGE_COST = 50

WEIGHT_1 = 2
WEIGHT_2 = 2.5
VOLUME_1 = 12
VOLUME_2 = 16
DISTANCE_1 = 100000
DISTANCE_2 = 120000

CHARGE_TIME = 30


class SeqDict(dict):

    def __getitem__(self, item):
        if isinstance(item, tuple):
            a = item[0] if isinstance(item[0], tuple) else (item[0], )
            b = item[1] if isinstance(item[1], tuple) else (item[1], )
            try:
                return dict.__getitem__(self, (a[-1:], b[:1]))
            except TypeError:
                raise BaseException("SeqDict TypeError in: " + str(item))
        else:
            raise BaseException("SeqDict's key must be 2-tuple")


SeqTuple = namedtuple(
    "Seq",
    [
        "vehicle_type",
        "volume",
        "weight",
        "total_distance",
        "total_time",
        "time_len",
        "es",
        "ls",
        "ef",
        "lf",
        "wait",
        "charge_cnt",
        "cost"
    ]
)


class Seq(SeqTuple):

    def __add__(self, other):
        if isinstance(other, Seq):
            pass
        else:
            raise BaseException("Seq class can't be added with " + str(other))


def time_transformer(s):
    a = s.split(":")
    return int(a[0]) * 60 + int(a[1]) - 8 * 60


def read_data(number):
    if number == 1:
        dt = pd.read_csv("input_B/inputdistancetime_1_1601.txt")
        node = pd.read_csv("input_B/inputnode_1_1601.csv", sep="\t")
    elif number == 2:
        dt = pd.read_csv("input_B/inputdistancetime_2_1501.txt")
        node = pd.read_csv("input_B/inputnode_2_1501.csv", sep="\t")
    elif number == 3:
        dt = pd.read_csv("input_B/inputdistancetime_3_1401.txt")
        node = pd.read_csv("input_B/inputnode_3_1401.csv", sep="\t")
    elif number == 4:
        dt = pd.read_csv("input_B/inputdistancetime_4_1301.txt")
        node = pd.read_csv("input_B/inputnode_4_1301.csv", sep="\t")
    elif number == 5:
        dt = pd.read_csv("input_B/inputdistancetime_5_1201.txt")
        node = pd.read_csv("input_B/inputnode_5_1201.csv", sep="\t")
    else:
        return None

    from_to_node = list(zip(dt["from_node"].values, dt["to_node"].values))
    ds = SeqDict({
        ((k1,), (k2,)): v
        for (k1, k2), v in pd.Series(dt["distance"].values, index=from_to_node).items()
    })
    tm = SeqDict({
        ((k1,), (k2,)): v
        for (k1, k2), v in pd.Series(dt["spend_tm"].values, index=from_to_node).items()
    })
    del dt

    node.columns = [
        "ID",
        "type",
        "lng",
        "lat",
        "weight",
        "volume",
        "first",
        "last"
    ]

    node["first"] = node.loc[:, "first"].apply(lambda x: time_transformer(x) if x != "-" else 0)
    node["last"] = node.loc[:, "last"].apply(lambda x: time_transformer(x) if x != "-" else 960)

    delivery = node[node.type == 2]
    pickup = node[node.type == 3]
    charge = node[node.type == 4]
    del node
    return ds, tm, delivery, pickup, charge


def get_node_info(node, is_charge=False):

    node_id = {(x,) for x in node["ID"].values.tolist()}

    if is_charge:
        del node
        return node_id
    else:
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
        del node
        return node_id, weight, volume, first, last


def merge_seq_arrange_time(seq1, seq2, tm, first, last):
    pass


def check_merge_seq_available(seq1, seq2, ds, tm, first, last):
    pass


def check_seq_available(seq, ds, tm, first, last):
    result = 0
    is_type_1 = True if seq.vehicle_type == 1 else False

    # volume limit
    if seq.volume > (VOLUME_1 if is_type_1 else VOLUME_2):
        result = 2

    # weight limit
    if seq.weight > (WEIGHT_1 if is_type_1 else WEIGHT_2):
        result = 3

    # distance limit
    ds_limit = DISTANCE_1 if is_type_1 else DISTANCE_2
    if seq.total_distance + ds[(0, ), seq] + ds[seq, (0,)] > ds_limit:
        pass


    pass
