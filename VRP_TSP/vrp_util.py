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


class SeqInfo(SeqTuple):

    def __add__(self, other):
        if isinstance(other, SeqInfo):
            # TODO
            pass
        else:
            raise BaseException("SeqInfo class can't be added with " + str(other))


def merge_seq_arrange_time(seq1, seq2, seq1info, seq2info, tm):
    ef1 = seq1info.ef + tm[seq1, seq2]
    lf1 = seq1info.lf + tm[seq1, seq2]
    # wait time between 1 and 2 = max{es2 - lf1, 0}
    new_wait = max(seq2info.es - lf1, 0)
    if new_wait == 0:
        # new_seq es = max{ef1, es2} - time_len1 - t12
        es = max(ef1, seq2info.es) - seq1info.time_len - tm[seq1, seq2]
        # new_seq ls = min{lf1, ls2} - time_len1 -t12
        ls = min(lf1, seq2info.ls) - seq1info.time_len - tm[seq1, seq2]
    else:
        es = seq1info.es
        ls = seq1info.es
    # new_seq time_len = time_len1 + 30 + t12 + wait + time_len2
    time_len = seq1info.time_len + tm[seq1, seq2] + new_wait + seq2info.time_len
    # new_seq wait time
    total_wait = seq1info.wait + seq2info.wait + new_wait
    return time_len, es, ls, es + time_len, ls + time_len, total_wait


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


def check_merge_seq_available(seq1, seq2, seq1info, seq2info, ds, tm):
    if seq1info.vehicle_type != seq2info.vehicle_type:
        return False, 1
    is_type_1 = True if seq1info.vehicle_type == 1 else False
    if seq1info.volume + seq2info.volume > (VOLUME_1 if is_type_1 else VOLUME_2):
        return False, 2
    if seq1info.weight + seq2info.weight > (WEIGHT_1 if is_type_1 else WEIGHT_2):
        return False, 3
    ds_limit = DISTANCE_1 if is_type_1 else DISTANCE_2
    if seq1info.total_distance + seq2info.total_distance +\
            ds[(0,), seq1] + ds[seq2, (0,)] > ds_limit:
        return False, 4
    if seq1info.ef + tm[seq1, seq2] > seq2info.ls:
        return False, 5
    return True, 0


def check_seq_available(seq, seq_info, ds, tm, first, last):
    is_type_1 = True if seq_info.vehicle_type == 1 else False
    if seq_info.volume > (VOLUME_1 if is_type_1 else VOLUME_2):
        return False, 2
    if seq_info.weight > (WEIGHT_1 if is_type_1 else WEIGHT_2):
        return False, 3
    ds_limit = DISTANCE_1 if is_type_1 else DISTANCE_2
    if seq_info.total_distance + ds[(0,), seq] + ds[seq, (0,)] > ds_limit:
        return False, 4
    if seq_info.total_time + tm[(0,), seq] + tm[seq, (0,)] > 960 or \
            seq_info.lf + tm[seq, (0,)] > 960 or \
            seq_info.ls - tm[(0,), seq] < 0:
        return False, 5
    return True, 0


def merge_seqs(seq1, seq2, tm, first, last):
    pass