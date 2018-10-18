import pandas as pd

from vrp.common.model import SeqDict


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
        for (k1, k2), v in pd.Series(
            dt["distance"].values, index=from_to_node
        ).items()
    })
    tm = SeqDict({
        ((k1,), (k2,)): v
        for (k1, k2), v in pd.Series(
            dt["spend_tm"].values, index=from_to_node
        ).items()
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

    node["first"] = node.loc[:, "first"].apply(
        lambda x: time_transformer(x) if x != "-" else 0
    )
    node["last"] = node.loc[:, "last"].apply(
        lambda x: time_transformer(x) if x != "-" else 960
    )

    delivery = node[node.type == 2]
    pickup = node[node.type == 3]
    charge = node[node.type == 4]

    lng_lat = list(zip(node["lng"].values, node["lat"].values))
    position = pd.Series(lng_lat, index=node["ID"]).to_dict()

    del node

    delivery_range = [delivery["ID"].min(), delivery["ID"].max()]
    pickup_range = [pickup["ID"].min(), pickup["ID"].max()]
    charge_range = [charge["ID"].min(), charge["ID"].max()]
    return ds, tm, delivery, pickup, charge, position, \
        [
            lambda x:
                True if delivery_range[0] <= x <= delivery_range[1] else False,
            lambda x:
                True if pickup_range[0] <= x <= pickup_range[1] else False,
            lambda x:
                True if charge_range[0] <= x <= charge_range[1] else False
        ]


def get_node_info(node, is_charge=False):
    node_id = {(x,) for x in node["ID"].values.tolist()}
    if is_charge:
        # weight = {
        #     (k,): 0
        #     for k, v in pd.Series(
        #         node["weight"].values, index=node["ID"].values
        #     ).items()
        # }
        # volume = {
        #     (k,): 0
        #     for k, v in pd.Series(
        #         node["volume"].values, index=node["ID"].values
        #     ).items()
        # }
        volume, weight = None, None
        first = {
            (k,): 0
            for k, v in pd.Series(
                node["first"].values, index=node["ID"].values
            ).items()
        }
        last = {
            (k,): 960
            for k, v in pd.Series(
                node["last"].values, index=node["ID"].values
            ).items()
        }
    else:
        weight = {
            (k,): float(v)
            for k, v in pd.Series(
                node["weight"].values, index=node["ID"].values
            ).items()
        }
        volume = {
            (k,): float(v)
            for k, v in pd.Series(
                node["volume"].values, index=node["ID"].values
            ).items()
        }
        first = {
            (k,): int(v)
            for k, v in pd.Series(
                node["first"].values, index=node["ID"].values
            ).items()
        }
        last = {
            (k,): int(v)
            for k, v in pd.Series(
                node["last"].values, index=node["ID"].values
            ).items()
        }
    del node
    return node_id, volume, weight, first, last
