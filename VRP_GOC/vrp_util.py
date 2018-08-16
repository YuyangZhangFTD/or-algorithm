from vrp_structure import SeqInfo
from vrp_constant import *
from vrp_cost import calculate_each_cost


def generate_node_type_function(size_list):
    return lambda x: True if 0 < x <= size_list[0] else False, \
        lambda x: True if size_list[0] < x <= size_list[0] + size_list[1] else False, \
        lambda x: True if size_list[0] + size_list[1] < x <= sum(size_list) else False


def schedule_time(seq1, seq2, seq1info, seq2info, tm):
    """
    schedule time with seq1 and seq2
    return time schedule of new seq
    :param seq1:
    :param seq2:
    :param seq1info:
    :param seq2info:
    :param tm:
    :return: time_len, es, ls, ef, lf, total_wait
    """
    ef1 = seq1info.ef + tm[seq1, seq2]
    lf1 = seq1info.lf + tm[seq1, seq2]
    # wait time between 1 and 2 = max{es2 - lf1, 0}
    new_wait = max(seq2info.es - lf1, 0)
    if new_wait == 0:
        # new_seq es = max{ef1, es2} - time_len1 - t12
        es = max(ef1, seq2info.es) - seq1info.time_len - tm[seq1, seq2]
        # new_seq ls = min{lf1, ls2} - time_len1 -t12
        ls = min(lf1, seq2info.ls) - seq1info.time_len - tm[seq1, seq2]
    else:
        es = seq1info.es
        ls = seq1info.es
    # new_seq time_len = time_len1 + 30 + t12 + wait + time_len2
    time_len = seq1info.time_len + tm[seq1, seq2] + new_wait + seq2info.time_len
    # new_seq wait time
    total_wait = seq1info.wait + seq2info.wait + new_wait
    return time_len, es, ls, es + time_len, ls + time_len, total_wait


def generate_seq_info(seq, ds, tm, volume, weight, first, last, judge_node_type_functions):
    """
    generate seq info from seq
    return SeqInfo(vehicle_type, volume, weight, total_distance,
        time_len, es, ls, ef, lf, wait, charge_cnt, cost)
    :param seq:
    :param ds:
    :param tm:
    :param volume:
    :param weight:
    :param first:
    :param last:
    :param judge_node_type_functions:
    :return:
    """
    is_delivery, is_pickup, is_charge = judge_node_type_functions
    # init volume and weight
    delivery_node = list(filter(lambda x: is_delivery(x), seq))
    charge_cnt = sum(filter(lambda x: is_charge(x), seq))
    init_volume = sum([volume[(x, )] for x in delivery_node])
    init_weight = sum([weight[(x, )] for x in delivery_node])

    node1 = seq[:1]
    current_distance = ds[(0,), node1]      # leave depot
    time_len = SERVE_TIME
    es = first[node1]
    ls = last[node1]
    ef = es + time_len
    lf = ls + time_len
    total_wait = 0
    current_volume = init_volume
    current_weight = init_weight
    charge_cnt = 0
    for i in range(1, len(seq)):
        node2 = seq[i, i+1]
        current_distance += ds[node1, node2]

        if is_delivery(node2[0]):
            current_volume -= volume[node2]
            current_weight -= weight[node2]
        elif is_pickup(node2[0]):
            current_volume += volume[node2]
            current_weight += weight[node2]

        ef += tm[node1, node2]
        lf += tm[node1, node2]
        wait = max(first[node2] - lf, 0)
        if wait == 0:
            es = max(ef, first[node2]) - time_len - tm[node1, node2]
            ls = min(lf, last[node2]) - time_len - tm[node1, node2]
        else:
            es = ls
            ls = ls
        time_len += wait + tm[node1, node2] + SERVE_TIME
        total_wait += wait
        ef = es + time_len
        lf = ls + time_len

        # TODO: judge vehicle type and charge_cnt

        node1 = node2

    current_distance += ds[node1, (0,)]     # get back to depot

    vehicle_type = 2

    return SeqInfo(
        vehicle_type, init_volume, init_weight,
        current_distance, time_len,
        es, ls, ef, lf, total_wait,
        charge_cnt, sum(calculate_each_cost(
            current_distance, vehicle_type, total_wait, charge_cnt
        ))
    )


def generate_route_info(seq, ds, tm, volume, weight):
    """
    generate route info from seq without use info
    return RouteInfo(vehicle_type, route(dist_seq), leave_time, arrive_time,
        distance, trans_cost, charge_cost, wait_cost, fixed use cost,
        total cost, charge_cnt)
    :param seq:
    :param ds:
    :param tm:
    :param volume:
    :param weight:
    :return:
    """
    pass
