from vrp_model import SeqInfo
from vrp_util import generate_seq_info
from vrp_construction import best_accept_insertion


def two_opt(
    seq, info: SeqInfo, ds, tm,
    volume, weight, first, last, node_type_judgement,
    iter_num=15
):
    """
    2-opt (2-exchange, Two-point Move):
        swap the position of two nodes
    :param seq:
    :param info:
    :param ds:
    :param tm:
    :param volume:
    :param weight:
    :param first:
    :param last:
    :param node_type_judgement:
    :param iter_num:
    :return:
    """
    if len(seq) <= 2:
        return seq, info
    else:
        tmp_seq = seq
        tmp_info = info
        for _ in range(iter_num):
            for i in range(len(seq) - 1):
                for j in range(i+1, len(seq)):
                    new_seq = seq[:i] + seq[i:j+1][::-1] + seq[j+1:]
                    try:
                        info = generate_seq_info(
                            new_seq, ds, tm, volume, weight,
                            first, last, node_type_judgement
                        )
                    except KeyError:
                        continue
                    if info is None:
                        continue
                    else:
                        if info.cost < tmp_info.cost:
                            tmp_seq = new_seq
                            tmp_info = info

        return tmp_seq, tmp_info


def or_opt(
    seq, info: SeqInfo, ds, tm,
    volume, weight, first, last,
    node_type_judgement, node_id_c
):
    """
    or-opt operator (or-opt move):

    :param seq:
    :param info:
    :param ds:
    :param tm:
    :param volume:
    :param weight:
    :param first:
    :param last:
    :param node_type_judgement:
    :param node_id_c:
    :return:
    """
    total_len = len(seq)
    old_cost = info.cost
    if total_len == 2:
        new_seq = seq[-1:] + seq[:1]
        new_info = generate_seq_info(
            new_seq, ds, tm, volume, weight,
            first, last, node_type_judgement
        )
        if new_info is not None and new_info.cost < old_cost:
            return new_seq, new_info
    elif total_len > 2:
        rank_list = []
        for sub_seq_len in range(1, total_len):
            for i in range(total_len):
                if i + sub_seq_len > total_len:
                    continue
                sub_seq = seq[i:i+sub_seq_len]
                main_seq = seq[:i] + seq[i+sub_seq_len:]
                try:
                    new_seq, new_info = best_accept_insertion(
                        sub_seq, main_seq, ds, tm, volume, weight,
                        first, last, node_type_judgement, node_id_c
                    )
                except KeyError:
                    continue
                if new_info is not None:
                    rank_list.append((new_seq, new_info, new_info.cost))
        if len(rank_list) > 0:
            rank_list.sort(key=lambda x: x[-1])
            if old_cost > rank_list[0][1].cost:
                return rank_list[0][0], rank_list[0][1]
    return seq, info


def two_opt_star(
    seq1, info1: SeqInfo, seq2, info2: SeqInfo,
    ds, tm, volume, weight, first, last,
    node_type_judgement,
    iter_num=15
):
    """
    2-opt* (2-opt* exchange, 2-opt move):
        remove two edges from the solution and
        replace them with two new edges
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param ds:
    :param tm:
    :param volume:
    :param weight:
    :param first:
    :param last:
    :param node_type_judgement:
    :param iter_num:
    :return:
    """
    have_updated = False
    tmp_seq1 = seq1
    tmp_info1 = info1
    tmp_seq2 = seq2
    tmp_info2 = info2
    for _ in range(iter_num):
        old_cost = tmp_info1.cost + tmp_info2.cost
        for i in range(1, len(tmp_seq1)-1):
            for j in range(1, len(tmp_seq2)-1):
                new_seq1 = tmp_seq1[:i] + tmp_seq2[j:]
                try:
                    new_info1 = generate_seq_info(
                        new_seq1, ds, tm, volume, weight,
                        first, last, node_type_judgement
                    )
                except KeyError:
                    continue
                if new_info1 is None:
                    continue
                new_seq2 = tmp_seq2[:j] + tmp_seq1[i:]
                try:
                    new_info2 = generate_seq_info(
                        new_seq2, ds, tm, volume, weight,
                        first, last, node_type_judgement
                    )
                except KeyError:
                    continue
                if new_info2 is None:
                    continue
                new_cost = new_info1.cost + new_info2.cost
                if old_cost > new_cost:
                    have_updated = True
                    tmp_seq1 = new_seq1
                    tmp_info1 = new_info1
                    tmp_seq2 = new_seq2
                    tmp_info2 = new_info2
                    break
            if have_updated:
                break
    return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)


def relocate(
    seq1, info1: SeqInfo, seq2, info2: SeqInfo,
    ds, tm, volume, weight, first, last,
    node_type_judgement,
    iter_num=15
):
    """
    relocate operator (One-point Move):
        move a customer visit from one route to another
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param ds:
    :param tm:
    :param volume:
    :param weight:
    :param first:
    :param last:
    :param node_type_judgement:
    :param iter_num:
    :return:
    """
    pass


def cross_exchange(
    seq1, info1: SeqInfo, seq2, info2: SeqInfo,
    ds, tm, volume, weight, first, last,
    node_type_judgement,
    iter_num=15
):
    """
    cross exchange
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param ds:
    :param tm:
    :param volume:
    :param weight:
    :param first:
    :param last:
    :param node_type_judgement:
    :param iter_num:
    :return:
    """
    pass
