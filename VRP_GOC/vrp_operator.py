from vrp_structure import SeqInfo
from vrp_cost import calculate_each_cost
from vrp_util import schedule_time_


# def merge_seqs(seq1, seq2, seq1info, seq2info, ds, tm):
#     """
#     merge seq1 and seq2 by adding
#     without considering whether seq1 or seq2 is available
#     return new seq and info
#     :param seq1: tuple
#     :param seq2: tuple
#     :param seq1info: SeqInfo
#     :param seq2info: SeqInfo
#     :param ds: dict
#     :param tm: dict
#     :return:
#     """
#     seq = seq1 + seq2
#     vehicle_type = seq1info.vehicle_type
#     volume = seq1info.volume + seq2info.volume
#     weight = seq1info.weight + seq2info.weight
#     charge_cnt = seq1info.charge_cnt + seq2info.charge_cnt
#     time_len, es, ls, ef, lf, total_wait = schedule_time_(seq1 + seq2, seq1info, seq2info, tm)
#     total_distance = ds[(0,), seq] + ds[seq, (0,)]
#     nid1 = seq[:1]
#     for i in range(1, len(seq)):
#         nid2 = seq[i:i + 1]
#         total_distance += ds[nid1, nid2]
#         nid1 = nid2
#     info = SeqInfo(
#         vehicle_type, volume, weight,
#         total_distance, time_len,
#         es, ls, ef, lf, total_wait,
#         charge_cnt, sum(calculate_each_cost(
#             total_distance, vehicle_type, total_wait, charge_cnt
#         ))
#     )
#     return seq, info
