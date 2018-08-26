from vrp_constant import *


def check_concat_seqs_available(seq1, seq2, seq1info, seq2info, ds, tm):
    """
    check whether to merge seq1 and seq2 is available
    without considering whether seq1 or seq2 is available
    return True or False and error code
    :param seq1:
    :param seq2:
    :param seq1info:
    :param seq2info:
    :param ds:
    :param tm:
    :return:
    """
    if seq1info.vehicle_type != seq2info.vehicle_type:
        return False, 1
    is_type_1 = True if seq1info.vehicle_type == 1 else False
    if seq1info.volume + seq2info.volume > (VOLUME_1 if is_type_1 else VOLUME_2):
        return False, 2
    if seq1info.weight + seq2info.weight > (WEIGHT_1 if is_type_1 else WEIGHT_2):
        return False, 3
    ds_limit = DISTANCE_1 if is_type_1 else DISTANCE_2
    if seq1info.total_distance + seq2info.total_distance - \
            ds[seq1, (0,)] - ds[(0,), seq2] + ds[seq1, seq2] \
            > ds_limit * (seq1info.charge_cnt + seq2info.charge_cnt + 1):
        return False, 4
    if seq1info.ef - tm[seq1, (0,)] + tm[seq1, seq2] > seq2info.ls + tm[(0,), seq2] + 0:
        return False, 5
    return True, 0


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
