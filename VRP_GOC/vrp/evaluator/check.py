from vrp.util.info import calculate_seq_distance
from vrp.common.constant import *

from functools import reduce
from typing import Tuple
from vrp.model import SeqInfo, Param


def check_concat_seqs_available(
        seq1: Tuple[int],
        info1: SeqInfo,
        seq2: Tuple,
        info2: SeqInfo,
        param: Param
):
    """
    check whether to merge seq1 and seq2 is available
    without considering whether seq1 or seq2 is available
    return True or False and error code
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param param:
    :return:
    """
    ds, tm, *_ = param
    if info1.vehicle_type != info2.vehicle_type:
        return False, 1
    is_type_1 = True if info1.vehicle_type == 1 else False
    if info1.volume + info2.volume > \
            (VOLUME_1 if is_type_1 else VOLUME_2):
        return False, 2
    if info1.weight + info2.weight > \
            (WEIGHT_1 if is_type_1 else WEIGHT_2):
        return False, 3
    _, (*_, dist1) = calculate_seq_distance(seq1, param)
    _, (dist2, *_) = calculate_seq_distance(seq2, param)
    ds_limit = DISTANCE_1 if is_type_1 else DISTANCE_2
    if dist1 + dist2 - ds[seq1, (0,)] - ds[(0,), seq2] + ds[seq1, seq2] \
            > ds_limit:
        return False, 4
    if info1.eps_list[-2] + SERVE_TIME + tm[seq1, seq2] > info2.lps_list[1]:
        return False, 5
    return True, 0


def check_seq_available(
        seq: Tuple[int],
        info: SeqInfo,
        param: Param
) -> (bool, int):
    ds, tm, volume, weight, first, last, _, _ = param

    is_type2 = True if info.vehicle_type == 2 else False
    volume_limit = VOLUME_2 if is_type2 else VOLUME_1
    weight_limit = WEIGHT_2 if is_type2 else WEIGHT_1
    distance_limit = DISTANCE_2 if is_type2 else DISTANCE_1

    # volume check
    if sum((volume[x] for x in ((x,) for x in seq))) > volume_limit:
        return False, 2

    # weight check
    if sum((weight[x] for x in ((x,) for x in seq))) > weight_limit:
        return False, 3

    # distance check
    _, dist_list = calculate_seq_distance(seq, param)
    if any(filter(lambda x: x > distance_limit, dist_list)):
        return False, 4

    # time window check
    #   1. check eps and lps
    #   2. check eps <= lps <= ls
    if not all((
        x[0] <= x[1] <= last[(x[2],)]
        for x in zip(info.eps_list, info.lps_list, seq)
    )):
        return False, 5

    return True, 0


# TODO
def check_output(route_dict, is_charge):
    all_nodes = [
        x
        for x in
        reduce(lambda x, y: x + y, [x for x in route_dict])
        if not is_charge(x)
    ]
    if len(all_nodes) == len(set(all_nodes)):
        return True
    else:
        return False


def violated_reason(violated_code):
    if violated_code == 1:
        print("vehicle type is not same")
    elif violated_code == 2:
        print("over weight limit")
    elif violated_code == 3:
        print("over volume limit")
    elif violated_code == 4:
        print("over distance limit")
    elif violated_code == 5:
        print("over time window limit")
