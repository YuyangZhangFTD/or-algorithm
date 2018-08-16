from vrp_structure import SeqInfo
from vrp_cost import calculate_each_cost


def merge_seqs(seq1, seq2, seq1info, seq2info, new_seq_time_info, ds, tm):
    """
    merge seq1 and seq2 by adding
    without considering whether seq1 or seq2 is available
    return new seq and info
    :param seq1:
    :param seq2:
    :param seq1info:
    :param seq2info:
    :param new_seq_time_info:
    :param ds:
    :param tm:
    :return:
    """
    seq = seq1 + seq2
    vehicle_type = seq1info.vehicle_type
    volume = seq1info.volume + seq2info.volume
    weight = seq1info.weight + seq2info.weight
    charge_cnt = seq1info.charge_cnt + seq2info.charge_cnt
    time_len, es, ls, ef, lf, total_wait = new_seq_time_info
    total_distance = ds[(0,), seq] + ds[seq, (0,)]
    nid1 = seq[:1]
    for i in range(1, len(seq)):
        nid2 = seq[i:i + 1]
        total_distance += ds[nid1, nid2]
        nid1 = nid2
    info = SeqInfo(
        vehicle_type, volume, weight,
        total_distance, time_len,
        es, ls, ef, lf, total_wait,
        charge_cnt, sum(calculate_each_cost(
            total_distance, vehicle_type, total_wait, charge_cnt
        ))
    )
    return seq, info
