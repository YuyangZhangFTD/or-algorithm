from vrp_util import generate_seq_info
from vrp_check import check_concat_seqs_available

from random import choice


def construct_saving_value_pair_candidate(
    candidate_seqs, route_dict, ds, tm, volume, weight,
    first, last, node_type_judgement, node_id_c,
    time_sorted_limit=False
):
    """

    :param candidate_seqs: candidate nodes or seqs
    :param route_dict: for saving result
    :param ds:
    :param tm:
    :param volume:
    :param weight:
    :param first:
    :param last:
    :param node_type_judgement:
    :param node_id_c:
    :param time_sorted_limit:
    :return:
    """
    saving_value_pair_candidate_dict = dict()
    for seq1 in candidate_seqs:
        for seq2 in candidate_seqs:
            if seq1 == seq2:
                continue

            if time_sorted_limit and \
                    (first[seq1], last[seq1]) <= (first[seq2], last[seq2]):
                is_available, err = check_concat_seqs_available(
                    seq1, seq2, route_dict[seq1],
                    route_dict[seq2],
                    ds, tm
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
                    new_seq, ds, tm, volume, weight,
                    first, last, node_type_judgement,
                    vehicle_type=2
                )
                if new_info is not None:
                    saving_value_pair_candidate_dict[(seq1, seq2)] = (
                        new_seq, new_info, old_cost - new_info.cost
                    )

    return saving_value_pair_candidate_dict


def saving_value_construct(
    candidate_seqs, route_dict, ds, tm, volume, weight,
    first, last, node_type_judgement, node_id_c,
    time_sorted_limit=False, merge_seq_each_time=100
):
    """

    :param candidate_seqs: candidate nodes or seqs
    :param route_dict: for saving result
    :param ds:
    :param tm:
    :param volume:
    :param weight:
    :param first:
    :param last:
    :param node_type_judgement:
    :param node_id_c:
    :param time_sorted_limit:
    :param merge_seq_each_time:
    :return:
    """
    saving_value_pair_candidate_dict = construct_saving_value_pair_candidate(
        candidate_seqs, route_dict, ds, tm, volume, weight,
        first, last, node_type_judgement, node_id_c,
        time_sorted_limit=time_sorted_limit
    )

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
    new_route_dict = dict()
    pop_route_set = set()
    for seq1, seq2, new_seq, new_info, _ in saving_value_rank_list:
        if seq1 not in pop_route_set and \
                seq2 not in pop_route_set \
                and new_info is not None:

            if new_seq_count >= merge_seq_each_time:
                break

            if seq1 not in node_id_c:
                # route_dict.pop(seq1)
                pop_route_set.add(seq1)
            if seq2 not in node_id_c:
                # route_dict.pop(seq2)
                pop_route_set.add(seq2)

            new_route_dict[new_seq] = new_info
            new_seq_count += 1

            # TODO: is this useful?
            first[new_seq] = new_info.es
            last[new_seq] = new_info.ls
            weight[new_seq] = new_info.weight
            volume[new_seq] = new_info.volume

    return new_route_dict, new_seq_count


def insert_construct_i1(
    candidate_seqs, route_dict, ds, tm, volume, weight,
    first, last, node_type_judgement, node_id_c,

):
    candidate_seqs = list(route_dict.keys())
    new_seq_count = 0
    while True:
        seed_seq = choice(candidate_seqs)
        feasible_seq = route_dict[seed_seq]

        pass
    pass

