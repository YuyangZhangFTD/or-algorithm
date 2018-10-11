from vrp.model import Param
from vrp.constant import *

from typing import Tuple, List
from itertools import *


def schedule_time(
        seq: Tuple,
        param: Param
) -> (List, List, float, float, float):
    """
    schedule a sequence
    :param seq:
    :param param:
    :return:
    """
    _, tm, _, _, first, last, ntj, _ = param
    _, _, is_charge = ntj
    node1 = (0,)
    serve_time = 0
    eps = 0  # early possible starting
    lps = 960  # latest possible starting
    total_shift = 0
    time_len = 0
    total_wait = 0
    total_delta = 0

    # init eps_list and lps_list
    eps_list = [0]
    lps_list = [960]

    for i in range(len(seq)):
        node2 = seq[i:i + 1]

        shift = max(0, lps + tm[node1, node2] + serve_time - last[node2])

        # lps: lps_node2
        if shift > 0:
            lps = last[node2]
            total_shift += shift
        else:
            lps += tm[node1, node2] + serve_time

        # check: if lps_node1 < eps_node1, return None
        if lps - tm[node1, node2] - serve_time < eps:
            return None, None, None, None, None, None

        # update wait and lps_node2
        wait = max(0, first[node2] - lps)
        if wait > 0:
            total_wait += wait
            lps = first[node2]

        delta = max(
            0, first[node2] - eps - serve_time - tm[node1, node2]
        )
        total_delta += delta

        # eps: eps_node2
        eps = max(eps + serve_time + tm[node1, node2], first[node2])

        # update eps_list and lps_list
        if delta > 0 or wait > 0:
            eps_list = [x + delta - wait for x in eps_list]
        if shift > 0:
            lps_list = [x - shift for x in lps_list]
        eps_list.append(eps)
        lps_list.append(lps)

        # time_len += tm + serve + wait
        time_len += tm[node1, node2] + serve_time + wait

        # iter
        serve_time = SERVE_TIME
        node1 = node2

    time_len += SERVE_TIME + tm[node1, (0,)]  # back to depot

    eps_list.append(0 + total_delta - total_wait + time_len)
    lps_list.append(960 - total_shift + time_len)
    buffer = lps_list[0] - eps_list[0]

    return eps_list, lps_list, time_len, total_wait, buffer


def schedule_time_refactor(
        seq: Tuple,
        param: Param
) -> (List, List, float, float, float):
    _, tm, _, _, first, last, ntj, _ = param
    _, _, is_charge = ntj
    node1 = (0,)
    serve_time = 0
    eps = 0  # early possible starting
    lps = 960  # latest possible starting
    total_shift = 0
    time_len = 0
    total_wait = 0
    total_delta = 0

    tuple_seq = tuple(zip((0, *seq, 0)))
    tm_edge = tuple(map(lambda x: tm[x], zip(tuple_seq[:-1], tuple_seq[1:])))

    # lps
    lps = (960,) + tuple(map(
        lambda n1, n2, t12: min(last[n1] + t12, last[n2]),
        tuple_seq[:-1], tuple_seq[1:], tm_edge
    ))
    shift = tuple(accumulate(
        tuple(map(
            lambda x, y, t: max(x + t - last[y], 0),
            lps[:-1], tuple_seq[1:], tm_edge
        ))[::-1]
    ))[::-1]
    lps = tuple(map(lambda x, y: x - y, lps, shift))

    # eps
    eps = (0,) + tuple(map(
        lambda n1, n2, t12: max(first[n1] + t12, first[n2]),
        tuple_seq[:-1], tuple_seq[1:], tm_edge
    ))
    delta = sum(map(
        lambda n1, n2, t12: max(first[n2] - first[n1] - t12, 0),
        tuple_seq[:-1], tuple_seq[1:], tm_edge
    ))
    pass
