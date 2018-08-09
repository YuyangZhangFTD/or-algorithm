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


SeqInfo = namedtuple(
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


def check_merge_seqs_available(seq1, seq2, seq1info, seq2info, ds, tm):
    if seq1info.vehicle_type != seq2info.vehicle_type:
        return False, 1
    is_type_1 = True if seq1info.vehicle_type == 1 else False
    if seq1info.volume + seq2info.volume > (VOLUME_1 if is_type_1 else VOLUME_2):
        return False, 2
    if seq1info.weight + seq2info.weight > (WEIGHT_1 if is_type_1 else WEIGHT_2):
        return False, 3
    ds_limit = DISTANCE_1 if is_type_1 else DISTANCE_2
    if seq1info.total_distance + seq2info.total_distance -\
            ds[seq1, (0,)] - ds[(0,), seq2] + ds[seq1, seq2] \
            > ds_limit:
        return False, 4
    if seq1info.ef + tm[seq1, seq2] > seq2info.ls:
        return False, 5
    return True, 0


def check_seq_available(seq, info, ds, tm):
    is_type_1 = True if info.vehicle_type == 1 else False
    if info.volume > (VOLUME_1 if is_type_1 else VOLUME_2):
        return False, 2
    if info.weight > (WEIGHT_1 if is_type_1 else WEIGHT_2):
        return False, 3
    ds_limit = DISTANCE_1 if is_type_1 else DISTANCE_2
    if info.total_distance + ds[(0,), seq] + ds[seq, (0,)] > ds_limit:
        return False, 4
    if info.total_time + tm[(0,), seq] + tm[seq, (0,)] > 960 or \
            info.lf + tm[seq, (0,)] > 960 or \
            info.ls - tm[(0,), seq] < 0:
        return False, 5
    return True, 0


def calculate_each_cost(distance, vehicle_type, wait, charge_cnt):
    is_type_1 = True if vehicle_type == 1 else False
    trans_cost = distance * (TRANS_COST_1 if is_type_1 else TRANS_COST_2)
    fixed_cost = FIXED_COST_1 if is_type_1 else FIXED_COST_2
    wait_cost = WAIT_COST * wait
    charge_cost = charge_cnt * CHARGE_COST
    return trans_cost, fixed_cost, wait_cost, charge_cost


def calculate_info_cost(info):
    return calculate_each_cost(
        info.total_distance,
        info.vehicle_type,
        info.wait,
        info.charge_cnt
    )


def merge_seqs(seq1, seq2, seq1info, seq2info, ds, tm, *time_info):
    seq = seq1 + seq2
    vehicle_type = seq1info.vehicle_type
    volume = seq1info.volume + seq2info.volume
    weight = seq1info.weight + seq2info.weight
    charge_cnt = seq1info.charge_cnt + seq2info.charge_cnt
    time_len, es, ls, ef, lf, total_wait = time_info
    total_time = tm[(0,), seq] + tm[seq, (0,)] + time_len
    total_distance = ds[(0,), seq] + ds[seq, (0,)]
    nid1 = seq[:1]
    for i in range(1, len(seq)):
        nid2 = seq[i:i+1]
        total_distance += ds[nid1, nid2]
        nid1 = nid2
    info = SeqInfo(
        vehicle_type, volume, weight,
        total_distance, total_time,
        time_len, es, ls, ef, lf, total_wait,
        charge_cnt, sum(calculate_each_cost(
            total_distance, vehicle_type, total_wait, charge_cnt
        ))
    )
    return seq, info
