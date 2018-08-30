from vrp_util import generate_seq_info
from vrp_check import check_concat_seqs_available


def construct_saving_value_pair_candidate(
    nodes, ds, tm, volume, weight,
    first, last, node_type_judgement,
    node_id_c
):
    saving_value_pair_candidate = dict()
    nodes = [(nid,) for nid in nodes]
    route_dict = {
        seq: generate_seq_info(
            seq, ds, tm, volume, weight,
            first, last, node_type_judgement
        )
        for seq in nodes
    }
    for seq1 in nodes:
        for seq2 in nodes:
            if seq1 == seq2:
                continue
            is_available, err = check_concat_seqs_available(
                seq1, seq2, route_dict[seq1],
                route_dict[seq2],
                ds, tm
            )
            if is_available:
                new_seq = seq1 + seq2
            elif err == 4:
                charge_nodes = [(cid, ds[seq1, cid] + ds[cid, seq2]) for cid in node_id_c]
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
                saving_value_pair_candidate[(seq1, seq2)] = (new_seq, new_info, old_cost - new_info.cost)

    return saving_value_pair_candidate


def saving_value_construct(
    nodes, ds, tm, volume, weight,
    first, last, node_type_judgement,
    node_id_c
):
    """

    :param nodes:
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
    saving_value_pair_candidate = construct_saving_value_pair_candidate(
        nodes, ds, tm, volume, weight,
        first, last, node_type_judgement,
        node_id_c
    )

    pass


def insert_construct(
    nodes, ds, tm, volume, weight, first, last,
    node_type_judgement, vehicle_type=-1
):
    pass

