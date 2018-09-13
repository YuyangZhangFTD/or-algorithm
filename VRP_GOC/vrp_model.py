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
    "Seq",
    [
        "vehicle_type",
        "volume",
        "weight",
        "total_distance",
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
