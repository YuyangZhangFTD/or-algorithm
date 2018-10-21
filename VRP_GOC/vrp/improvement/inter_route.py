from vrp.common.model import SeqInfo, Param
from vrp.common.constant import M
from vrp.util.info import generate_seq_info
from vrp.util.insertion import insertion

import random
from typing import Tuple, Set


def two_opt_star(
        seq1: Tuple,
        info1: SeqInfo,
        seq2: Tuple,
        info2: SeqInfo,
        param: Param,
        best_accept: bool = True,
        better_accept: bool = True,
        probability: float = 0.8,
        infeasible: bool = False
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
    :param infeasible
    :return:
    """
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
    infeasible = False if better_accept or best_accept else infeasible
    tmp_seq1 = seq1[:]
    tmp_info1 = None
    tmp_seq2 = seq2[:]
    tmp_info2 = None
    tmp_cost = info1.cost + info2.cost \
        if info1 is not None and info2 is not None else M
    have_update = False
    while True:
        for i in range(1, len(tmp_seq1) - 1):
            for j in range(1, len(tmp_seq2) - 1):

                new_seq1 = tmp_seq1[:i] + tmp_seq2[j:]
                try:
                    new_info1 = generate_seq_info(new_seq1, param)
                except KeyError:
                    continue

                new_seq2 = tmp_seq2[:j] + tmp_seq1[i:]
                try:
                    new_info2 = generate_seq_info(new_seq2, param)
                except KeyError:
                    continue

                if new_info1 is None or new_info2 is None:
                    if infeasible and random.random() < probability:
                        return (new_seq1, new_info1), (new_seq2, new_info2)
                    continue
                if new_info1.cost + new_info2.cost < tmp_cost:
                    if best_accept:
                        tmp_seq1, tmp_info1 = new_seq1, new_info1
                        tmp_seq2, tmp_info2 = new_seq2, new_info2
                        tmp_cost = new_info1.cost + new_info2.cost
                        have_update = True
                        break
                    if better_accept:
                        return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
                if probability and random.random() < probability:
                    return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
            if have_update:
                break
        if not have_update:
            break
        have_update = False
    if tmp_info1 is None or tmp_info2 is None:
        if infeasible and random.random() < probability:
            return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
        return (None, None), (None, None)
    else:
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
        probability: float = 0.8,
        infeasible: bool = False
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
    :param infeasible
    :return:
    """
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
    infeasible = False if better_accept or best_accept else infeasible
    tmp_cost = info1.cost + info2.cost \
        if info1 is not None and info2 is not None else M
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
                node, seq_2, param, node_id_c, best_accept=True
            )

            if new_info1 is None or new_info2 is None:
                if infeasible and random.random() < probability:
                    return (new_seq1, new_info1), (new_seq2, new_info2)
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
        if infeasible and random.random() < probability:
            return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
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
        probability: float = 0.8,
        infeasible: bool = False
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
    :param infeasible
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
                    new_info2 = generate_seq_info(new_seq2, param)
                    if new_info1 is None or new_info2 is None:
                        if infeasible and random.random() < probability:
                            return (new_seq1, new_info1), (new_seq2, new_info2)
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
        if infeasible and random.random() < probability:
            return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
        return (None, None), (None, None)
    return (tmp_seq1, tmp_info1), (tmp_seq2, tmp_info2)
