from vrp.util.info import generate_seq_info
from vrp.common.model import SeqInfo, Param
from vrp.evaluator.check import check_concat_seqs_available

from typing import Dict, Tuple, Set


def generate_saving_value_pair_candidates(
        candidate_seqs: Set,
        route_dict: Dict[Tuple, SeqInfo],
        param: Param,
        node_id_c: Set,
        time_sorted_limit: bool = False
) -> Dict[Tuple, Tuple]:
    """
    :param candidate_seqs: candidate nodes or seqs
    :param route_dict: for saving result
    :param param:
    :param node_id_c:
    :param time_sorted_limit:
    :return:
    """
    ds, tm, volume, weight, first, last, ntj, position = param
    saving_value_pair_candidate_dict = dict()
    for seq1 in candidate_seqs:
        for seq2 in candidate_seqs:
            if seq1 == seq2:
                continue
            info1, info2 = route_dict[seq1], route_dict[seq2]

            if time_sorted_limit:
                if not (
                    (info1.eps_list[0], info1.lps_list[0]) <=
                    (info2.eps_list[0], info2.lps_list[0])
                ):
                    continue

            is_available, err = check_concat_seqs_available(
                seq1, route_dict[seq1], seq2, route_dict[seq2], param
            )

            if is_available:
                new_seq = seq1 + seq2
            elif err == 4:  # over distance limit
                charge_nodes = [
                    (cid, ds[seq1, cid] + ds[cid, seq2])
                    for cid in node_id_c
                ]
                charge_nodes.sort(key=lambda x: x[-1])
                new_seq = seq1 + charge_nodes[0][0] + seq2
                del charge_nodes
            else:
                continue

            old_cost = route_dict[seq1].cost + route_dict[seq2].cost
            new_info = generate_seq_info(
                new_seq, param, vehicle_type=2
            )
            if new_info is not None:
                saving_value_pair_candidate_dict[(seq1, seq2)] = (
                    new_seq, new_info, old_cost - new_info.cost
                )

    return saving_value_pair_candidate_dict


def merge_saving_value_pairs(
        candidate_seqs: Set,
        route_dict: Dict[Tuple, SeqInfo],
        param: Param,
        node_id_c: Set,
        time_sorted_limit: bool = False,
        merge_seq_each_time: int = 100
) -> (Dict[Tuple, SeqInfo], int):
    saving_value_pair_candidate_dict = generate_saving_value_pair_candidates(
        candidate_seqs, route_dict, param, node_id_c,
        time_sorted_limit=time_sorted_limit
    )
    print(len(saving_value_pair_candidate_dict))

    saving_value_rank_list = []
    for (seq1, seq2), (new_seq, new_info, saving_value) in \
            saving_value_pair_candidate_dict.items():
        if saving_value > 0:
            saving_value_rank_list.append(
                (seq1, seq2, new_seq, new_info, saving_value)
            )
    del saving_value_pair_candidate_dict
    saving_value_rank_list.sort(key=lambda x: x[-1], reverse=True)

    new_seq_count = 0
    pop_route_set = set()
    for seq1, seq2, new_seq, new_info, _ in saving_value_rank_list:
        if seq1 not in pop_route_set and \
                seq2 not in pop_route_set \
                and new_info is not None:

            if new_seq_count >= merge_seq_each_time:
                break

            if seq1 not in node_id_c:
                route_dict.pop(seq1)
                pop_route_set.add(seq1)
            if seq2 not in node_id_c:
                route_dict.pop(seq2)
                pop_route_set.add(seq2)

            route_dict[new_seq] = new_info
            new_seq_count += 1

    return route_dict, new_seq_count


def saving_value_construct(
        candidate_seqs: Set,
        init_route_dict: Dict[Tuple, SeqInfo],
        param: Param,
        node_id_c: Set,
        time_sorted_limit: bool = False,
        merge_seq_each_time: int = 100
) -> Dict[Tuple, SeqInfo]:
    """

    :param candidate_seqs:
    :param init_route_dict:
    :param param:
    :param node_id_c:
    :param time_sorted_limit:
    :param merge_seq_each_time:
    :return:
    """
    # candidate_seqs = set(*candidate_seqs)
    route_dict = {
        k: v for k, v in init_route_dict.items()
        if k in candidate_seqs or k in node_id_c
    }
    while True:
        route_dict, new_seq_count = merge_saving_value_pairs(
            candidate_seqs, route_dict, param, node_id_c,
            time_sorted_limit=time_sorted_limit,
            merge_seq_each_time=merge_seq_each_time
        )
        # update candidate seqs
        candidate_seqs = list(route_dict)
        if new_seq_count < 1:
            break
    return route_dict
