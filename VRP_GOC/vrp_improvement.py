from vrp_model import SeqInfo, Param
from vrp_util import generate_seq_info
from vrp_construction import insertion

import random
from typing import Tuple, Set


def two_opt(
        seq: Tuple,
        info: SeqInfo,
        param: Param,
        iter_num: int = 15
) -> (Tuple, SeqInfo):
    """
    2-opt (2-exchange, Two-point Move):
        swap the position of two nodes
    :param seq:
    :param info:
    :param param:
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
                for j in range(i + 1, len(seq)):
                    new_seq = seq[:i] + seq[i:j + 1][::-1] + seq[j + 1:]
                    try:
                        info = generate_seq_info(
                            new_seq, param
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
        seq: Tuple,
        info: SeqInfo,
        param: Param,
        node_id_c: Set
) -> (Tuple, SeqInfo):
    """
    or-opt operator (or-opt move):

    :param seq:
    :param info:
    :param param:
    :param node_id_c:
    :return:
    """
    total_len = len(seq)
    old_cost = info.cost
    if total_len == 2:
        new_seq = seq[-1:] + seq[:1]
        new_info = generate_seq_info(
            new_seq, param
        )
        if new_info is not None and new_info.cost < old_cost:
            return new_seq, new_info
    elif total_len > 2:
        rank_list = []
        for sub_seq_len in range(1, total_len):
            for i in range(total_len):
                if i + sub_seq_len > total_len:
                    continue
                sub_seq = seq[i:i + sub_seq_len]
                main_seq = seq[:i] + seq[i + sub_seq_len:]
                try:
                    new_seq, new_info = insertion(
                        sub_seq, main_seq, param, node_id_c,
                        best_accept=True
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
        seq1: Tuple,
        info1: SeqInfo,
        seq2: Tuple,
        info2: SeqInfo,
        param: Param,
        iter_num: int = 15
) -> ((Tuple, SeqInfo), (Tuple, SeqInfo)):
    """
    2-opt* (2-opt* exchange, 2-opt move):
        remove two edges from the solution and
        replace them with two new edges
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param param:
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
        for i in range(1, len(tmp_seq1) - 1):
            for j in range(1, len(tmp_seq2) - 1):
                new_seq1 = tmp_seq1[:i] + tmp_seq2[j:]
                try:
                    new_info1 = generate_seq_info(
                        new_seq1, param
                    )
                except KeyError:
                    continue
                if new_info1 is None:
                    continue
                new_seq2 = tmp_seq2[:j] + tmp_seq1[i:]
                try:
                    new_info2 = generate_seq_info(
                        new_seq2, param
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
        seq1: Tuple,
        info1: SeqInfo,
        seq2: Tuple,
        info2: SeqInfo,
        param: Param,
        node_id_c: Set,
        best_accept: bool = True,
        probability: float = 0.8
) -> ((Tuple, SeqInfo), (Tuple, SeqInfo)):
    """
    relocate operator (One-point Move):
        move a customer visit from one route to another
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param param:
    :param node_id_c:
    :param best_accept:
    :param probability:
    :return:
    """
    tmp_cost = info1.cost + info2.cost
    tmp_seq1 = None
    tmp_seq2 = None
    tmp_info1 = None
    tmp_info2 = None
    for seq_1, seq_2 in [[seq1, seq2], [seq2, seq1]]:
        for i in range(len(seq1)):
            node = seq_1[i:i + 1]
            new_seq1, new_info1 = generate_seq_info(
                seq_1[:i] + seq_1[i + 1:], param
            )
            new_seq2, new_info2 = insertion(
                node, seq_2, param, node_id_c, best_accept, probability
            )
            if new_info1 is None or new_info1 is None:
                continue
            else:
                if best_accept:
                    if tmp_cost > new_info1.cost + new_info2.cost:
                        tmp_seq1, tmp_info1 = new_seq1, new_info1
                        tmp_seq2, tmp_info2 = new_seq2, new_info2
                else:
                    if random.random() < probability:
                        return (new_seq1, new_info1), (new_seq2, new_info2)
    if tmp_seq1 is None or tmp_seq2 is None:
        return (None, None), (None, None)
    return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)


def cross_exchange(
        seq1: Tuple,
        info1: SeqInfo,
        seq2: Tuple,
        info2: SeqInfo,
        param: Param,
        best_accept: bool = True,
        probability: float = 0.8
) -> ((Tuple, SeqInfo), (Tuple, SeqInfo)):
    """
    cross exchange
        first remove two edges (i−1, 􏰉i) and (k, 􏰉k+1) from a first route,
        while two edges (j−1􏰉, j), and (l,􏰉 l+1) are removed from second route.
        Then the segments i − k and j − l,
        which may contain an arbitrary number of customers,
        are swapped by introducing the new edges
        (i−1, j), (l, k+1), (j−1, i), and (k􏰉l+1)
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param param:
    :param best_accept:
    :param probability:
    :return:
    """
    tmp_cost = info1.cost + info2.cost
    tmp_seq1 = None
    tmp_info1 = None
    tmp_seq2 = None
    tmp_info2 = None
    for i in range(len(seq1)):
        for k in range(i, len(seq1)):
            for j in range(len(seq2)):
                for l in range(j, len(seq2)):
                    new_seq1 = seq1[:i] + seq2[j:l] + seq1[k:]
                    new_seq2 = seq2[:j] + seq1[i:k] + seq2[l:]
                    new_info1 = generate_seq_info(new_seq1, param)
                    if new_info1 is None:
                        continue
                    new_info2 = generate_seq_info(new_seq2, param)
                    if new_info2 is None:
                        continue
                    if best_accept:
                        if tmp_cost > new_info1.cost + new_info2.cost:
                            tmp_seq1, tmp_info1 = new_seq1, new_info1
                            tmp_seq2, tmp_info2 = new_seq2, new_info2
                    else:
                        if random.random() < probability:
                            return new_seq1, new_info1, new_seq2, new_info2
    if tmp_seq1 is None or tmp_seq2 is None:
        return (None, None), (None, None)
    else:
        return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
