from vrp.util.info import generate_seq_info
from vrp.common.model import SeqInfo, Param
from vrp.common.constant import *

import random
from typing import Tuple


def insertion(
        node: Tuple,
        seq: Tuple,
        param: Param,
        node_id_c: set,
        best_accept: bool = True,
        better_accept: bool = True,
        probability: float = 0.8
) -> (Tuple, SeqInfo):
    """

    :param node:
    :param seq:
    :param param:
    :param node_id_c:
    :param best_accept:
    :param better_accept:
    :param probability:
    :return:
    """
    tmp_cost = M
    tmp_seq = None
    tmp_info = None
    ds, *_ = param
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
    for i in range(len(seq)):
        new_seq = seq[:i] + node + seq[i:]
        new_info = generate_seq_info(
            new_seq, param, vehicle_type=2
        )
        if new_info is None:
            rank_list = [
                (cid, ds[node, cid] + ds[cid, seq[i:]])
                for cid in node_id_c
            ]
            rank_list.sort(key=lambda x: x[-1])
            for cid, _ in rank_list:
                new_info = generate_seq_info(
                    seq[:i] + node + cid + seq[i:],
                    param
                )
                if new_info is not None:
                    new_seq = seq[:i] + node + cid + seq[i:]
                    break
            else:
                continue

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


def efficient_insertion(
        node: Tuple,
        seq: Tuple,
        info: SeqInfo,
        param: Param,
        node_id_c: set,
        best_accept: bool = True,
        better_accept: bool = True,
        probability: float = 0.8
) -> (Tuple, SeqInfo):
    """

    :param node:
    :param seq:
    :param info:
    :param param:
    :param node_id_c:
    :param best_accept:
    :param better_accept:
    :param probability:
    :return:
    """
    tmp_cost = M
    tmp_seq = None
    tmp_info = None
    ds, *_ = param
    better_accept = False if best_accept else better_accept
    probability = 0 if better_accept or best_accept else probability
    for i in range(len(seq)):
        new_seq = seq[:i] + node + seq[i:]

        # new_info = generate_seq_info(
        #     new_seq, param, vehicle_type=2
        # )
        # TODO: generate new_info

        if new_info is None:
            rank_list = [
                (cid, ds[node, cid] + ds[cid, seq[i:]])
                for cid in node_id_c
            ]
            rank_list.sort(key=lambda x: x[-1])
            for cid, _ in rank_list:
                new_info = generate_seq_info(
                    seq[:i] + node + cid + seq[i:],
                    param
                )
                if new_info is not None:
                    new_seq = seq[:i] + node + cid + seq[i:]
                    break
            else:
                continue

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
