from vrp_structure import SeqInfo
from vrp_util import generate_seq_info


def two_opt(seq, info: SeqInfo, iter_num, ds, tm, volume, weight, first, last, node_type_judgement):
    if len(seq) <= 2:
        return seq, info
    else:
        tmp_seq = seq
        tmp_info = info
        for _ in range(iter_num):
            for i in range(len(seq) - 1):
                for j in range(i+1, len(seq)):
                    new_seq = seq[:i] + seq[i:j+1][::-1] + seq[j+1:]
                    info = generate_seq_info(
                        new_seq, ds, tm, volume, weight,
                        first, last, node_type_judgement
                    )
                    if info is None:
                        continue
                    else:
                        if info.cost < tmp_info.cost:
                            tmp_seq = new_seq
                            tmp_info = info

        return tmp_seq, tmp_info


def re_locate():
    pass


def or_opt():
    pass


def cross_exchange():
    pass
