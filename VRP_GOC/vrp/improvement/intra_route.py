from vrp.common.model import SeqInfo, Param
from vrp.common.constant import M
from vrp.util.info import generate_seq_info
from vrp.util.insertion import insertion

import random
from typing import Tuple, Set


def two_opt(
        seq: Tuple,
        info: SeqInfo,
        param: Param,
        best_accept: bool = True,
        better_accept: bool = True,
        probability: float = 0.8,
        infeasible: bool = False
) -> (Tuple, SeqInfo):
    """
    2-opt (2-exchange, Two-point Move):
        The edges (i, i+1) and (j, j+1) are replaced
        by edges (i, j) and (i+1, j+1),
        thus reversing the direction of customers between i+1 and j .
    :param seq:
    :param info:
    :param param:
    :param best_accept:
    :param better_accept:
    :param probability:
    :param infeasible:
    :return:
    """
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
    infeasible = False if better_accept or best_accept else infeasible
    tmp_seq = seq[:]
    tmp_info = None
    tmp_cost = info.cost if info is not None else M
    have_update = False
    while True:
        for i in range(len(tmp_seq) - 1):
            for j in range(i + 1, len(tmp_seq)):
                new_seq = tmp_seq[:i] + tmp_seq[i:j + 1][::-1] + tmp_seq[j + 1:]
                try:
                    new_info = generate_seq_info(new_seq, param)
                except KeyError:
                    continue
                if new_info is None:
                    if infeasible and random.random() < probability:
                        return new_seq, None
                    continue
                else:
                    if new_info.cost < tmp_cost:
                        if best_accept:
                            tmp_seq, tmp_info = new_seq, new_info
                            tmp_cost = new_info.cost
                            have_update = True
                            break
                        if better_accept:
                            return new_seq, new_info
                    if probability and random.random() < probability:
                        return new_seq, new_info
            if have_update:
                break
        if not have_update:
            break
        have_update = False
    if tmp_info is None:
        if infeasible and random.random() < probability:
            return tmp_seq, None
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
        probability: float = 0.8,
        infeasible: bool = False
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
    :param infeasible:
    :return:
    """
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
    infeasible = False if better_accept or best_accept else infeasible
    tmp_seq = seq[:]
    tmp_cost = info.cost if info is not None else M
    tmp_info = None
    if len(seq) <= 2:  # for efficiency
        return None, None
    have_update = False
    while True:
        for sub_seq_len in range(1, len(seq)):
            for i in range(len(seq)):
                if i + sub_seq_len > len(seq):
                    continue
                sub_seq = tmp_seq[i:i + sub_seq_len]
                main_seq = tmp_seq[:i] + tmp_seq[i + sub_seq_len:]
                try:
                    new_seq, new_info = insertion(
                        sub_seq, main_seq, param, node_id_c, best_accept=True
                    )
                except KeyError:
                    continue
                if new_info is None:
                    if infeasible and random.random() < probability:
                        return new_seq, None
                    continue
                else:
                    if new_info.cost < tmp_cost:
                        if best_accept:
                            tmp_seq, tmp_info = new_seq, new_info
                            tmp_cost = new_info.cost
                            have_update = True
                            break
                        if better_accept:
                            return new_seq, new_info
                    if probability and random.random() < probability:
                        return new_seq, new_info
            if have_update:
                break
        if not have_update:
            break
        have_update = False
    if tmp_info is None:
        if infeasible and random.random() < probability:
            return tmp_seq, None
        return None, None
    else:
        return tmp_seq, tmp_info
