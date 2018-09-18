from collections import namedtuple


class SeqDict(dict):

    def __getitem__(self, item):

        if len(item) != 2:
            return dict.__getitem__(self, item)
        else:
            a, b = item
            try:
                return dict.__getitem__(self, (a[-1:], b[:1]))
            except TypeError:
                raise BaseException("SeqDict TypeError in: " + str(item))


SeqInfo = namedtuple(
    "SeqInfo",
    [
        "vehicle_type",
        "volume",
        "weight",
        "total_distance",
        "eps_list",  # earliest possible start for every node [0, n1,..., 0]
        "lps_list",  # latest possible start for every node [0, n1,..., 0]
        "time_len",  # total time
        "wait",  # wait time
        "buffer",  # buffer time
        "charge_index",
        "cost"
    ]
)

Param = namedtuple(
    "Param",
    [
        "ds",
        "tm",
        "volume",
        "weight",
        "first",
        "last",
        "ntj",  # For node_type_judgement
        "position"
    ]
)
