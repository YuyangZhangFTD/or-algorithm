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


# SeqInfo_ = namedtuple(
#     "Seq",
#     [
#         "vehicle_type",
#         "volume",
#         "weight",
#         "total_distance",
#         "leave_time"
#         "arrive_time"
#         "wait",
#         "charge_cnt",
#         "cost"
#     ]
# )

RouteInfo = namedtuple(
    "Route",
    [
        "vehicle_type",
        "dist_seq",
        "distribute_lea_tm",
        "distribute_arr_tm",
        "distance",
        "trans_cost",
        "charge_cost",
        "wait_cost",
        "fixed_use_cost",
        "total_cost",
        "charge_cnt"
    ]
)
