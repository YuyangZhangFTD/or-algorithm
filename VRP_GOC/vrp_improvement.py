from vrp_model import SeqInfo, Param
from vrp_util import generate_seq_info
from vrp_construction import insertion

import random
from typing import Tuple, Set


def two_opt(
        seq: Tuple,
        info: SeqInfo,
        param: Param,
        best_accept: bool = True,
        better_accept: bool = True,
        probability: float = 0.8
) -> (Tuple, SeqInfo):
    """
    2-opt (2-exchange, Two-point Move):
        The edges (i, i+1) and (j, j+1) are replaced
        by edges (i, j􏰂) and (i+1, j+1),
        thus reversing the direction of customers between i+1 and j .
    :param seq:
    :param info:
    :param param:
    :param best_accept:
    :param better_accept:
    :param probability:
    :return:
    """
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
    tmp_seq = None
    tmp_info = None
    tmp_cost = info.cost
    for i in range(len(seq) - 1):
        for j in range(i + 1, len(seq)):
            new_seq = seq[:i] + seq[i:j + 1][::-1] + seq[j + 1:]
            try:
                new_info = generate_seq_info(new_seq, param)
            except KeyError:
                continue
            if new_info is None:
                continue
            else:
                if new_info.cost < tmp_cost:
                    if best_accept:
                        tmp_seq, tmp_info = new_seq, new_info
                        tmp_cost = new_info.cost
                        continue
                    if better_accept:
                        return new_seq, new_info
                if probability and random.random() < probability:
                    return new_seq, new_info
    if tmp_info is None:
        return None, None
    else:
        return tmp_seq, tmp_info


def or_opt(
        seq: Tuple,
        info: SeqInfo,
        param: Param,
        node_id_c: Set,
        best_accept: bool = True,
        better_accept: bool = True,
        probability: float = 0.8
) -> (Tuple, SeqInfo):
    """
    or-opt operator (or-opt move):
        Customers i and i + 1 are relocated to be served
        between two customers j and j + 1,
        instead of customers i − 1 and i + 2.
        This is performed by replacing three edges
        (i−1, i), (i+1, i+2), and (j, j+1)
        by the edges (i−1, i+2), (j, i), and (i+1, j+1),
        preserving the orientation of the route.
    :param seq:
    :param info:
    :param param:
    :param node_id_c:
    :param best_accept:
    :param better_accept:
    :param probability:
    :return:
    """
    tmp_cost = info.cost
    tmp_seq = None
    tmp_info = None
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
    if len(seq) <= 2:  # for efficiency
        return None, None
    for sub_seq_len in range(1, len(seq)):
        for i in range(len(seq)):
            if i + sub_seq_len > len(seq):
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
            if new_info is None:
                continue
            else:
                if new_info.cost < tmp_cost:
                    if best_accept:
                        tmp_seq, tmp_info = new_seq, new_info
                        tmp_cost = new_info.cost
                    if better_accept:
                        return new_seq, new_info
                if probability and random.random() < probability:
                    return new_seq, new_info
    if tmp_info is None:
        return None, None
    else:
        return tmp_seq, tmp_info


def two_opt_star(
        seq1: Tuple,
        info1: SeqInfo,
        seq2: Tuple,
        info2: SeqInfo,
        param: Param,
        best_accept: bool = True,
        better_accept: bool = True,
        probability: float = 0.8
) -> ((Tuple, SeqInfo), (Tuple, SeqInfo)):
    """
    2-opt* (2-opt* exchange, 2-opt move):
        The customers served after customer i on the upper route are reinserted
        to be served after customer j on the lower route,
        and customers after j on the lower route are moved to be served
        on the upper route after customer i.
        This is performed by replacing edges (i, i+1) and (j, j+1)
        with edges (i, j+1) and (j, i+1).
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param param:
    :param best_accept:
    :param better_accept:
    :param probability:
    :return:
    """
    tmp_cost = info1.cost + info2.cost
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
    tmp_seq1 = None
    tmp_info1 = None
    tmp_seq2 = None
    tmp_info2 = None
    for i in range(1, len(seq1) - 1):
        for j in range(1, len(seq2) - 1):
            new_seq1 = seq1[:i] + seq2[j:]
            try:
                new_info1 = generate_seq_info(new_seq1, param)
            except KeyError:
                continue
            if new_info1 is None:
                continue
            new_seq2 = seq2[:j] + seq1[i:]
            try:
                new_info2 = generate_seq_info(new_seq2, param)
            except KeyError:
                continue
            if new_info2 is None:
                continue
            if new_info1.cost + new_info2.cost < tmp_cost:
                if best_accept:
                    tmp_seq1, tmp_info1 = new_seq1, new_info1
                    tmp_seq2, tmp_info2 = new_seq2, new_info2
                    tmp_cost = new_info1.cost + new_info2.cost
                if better_accept:
                    return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
            if probability and random.random() < probability:
                return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
    return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)


def relocate(
        seq1: Tuple,
        info1: SeqInfo,
        seq2: Tuple,
        info2: SeqInfo,
        param: Param,
        node_id_c: Set,
        best_accept: bool = True,
        better_accept: bool = True,
        probability: float = 0.8
) -> ((Tuple, SeqInfo), (Tuple, SeqInfo)):
    """
    relocate operator (One-point Move):
        The edges (i−1, i), (i, i+1), and (j, j+1) are replaced
        by (i−1, i+1), (j, i), and (i, j+1), i.e.,
        customer i from the origin route is placed into the destination route.
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param param:
    :param node_id_c:
    :param best_accept:
    :param better_accept:
    :param probability:
    :return:
    """
    tmp_cost = info1.cost + info2.cost
    tmp_seq1 = None
    tmp_seq2 = None
    tmp_info1 = None
    tmp_info2 = None
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
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
                if new_info1.cost + new_info2.cost < tmp_cost:
                    if best_accept:
                        tmp_seq1, tmp_info1 = new_seq1, new_info1
                        tmp_seq2, tmp_info2 = new_seq2, new_info2
                    if better_accept:
                        return (new_seq1, new_info1), (new_seq2, new_info2)
                if probability and random.random() < probability:
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
        better_accept: bool = True,
        probability: float = 0.8
) -> ((Tuple, SeqInfo), (Tuple, SeqInfo)):
    """
    cross exchange
        Segments (i, k) on the upper route and
        (j, l) on the lower route are simultaneously reinserted
        into the lower and upper routes, respectively.
        This is performed by replacing edges (i-1, i), (k, k+1), (j−1, j),
        and (l, l+1) by edges (i−1, j), (l, k+1), (j−1, i),and (k, l+1).
        Note that the orientation of both routes is preserved.
    :param seq1:
    :param info1:
    :param seq2:
    :param info2:
    :param param:
    :param best_accept:
    :param better_accept:
    :param probability:
    :return:
    """
    tmp_cost = info1.cost + info2.cost
    tmp_seq1 = None
    tmp_info1 = None
    tmp_seq2 = None
    tmp_info2 = None
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
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
                    else:
                        if new_info1.cost + new_info2.cost < tmp_cost:
                            if best_accept:
                                tmp_seq1, tmp_info1 = new_seq1, new_info1
                                tmp_seq2, tmp_info2 = new_seq2, new_info2
                            if better_accept:
                                return (new_seq1, new_info1), \
                                       (new_seq2, new_info2)
                        if probability and random.random() < probability:
                            return (new_seq1, new_info1), (new_seq2, new_info2)
    if tmp_seq1 is None or tmp_seq2 is None:
        return (None, None), (None, None)
    return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
