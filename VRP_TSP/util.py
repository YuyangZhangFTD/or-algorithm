TRANS_COST_1 = 12 / 1000
TRANS_COST_2 = 14 / 1000
FIXED_COST_1 = 200
FIXED_COST_2 = 300
WAIT_COST = 24 / 60
CHARGE_COST = 50

WEIGHT_1 = 2
WEIGHT_2 = 2.5
VOLUME_1 = 12
VOLUME_2 = 16
DISTANCE_1 = 100000
DISTANCE_2 = 120000

M = 1e15


def route2seq(route):
    return tuple(route[1:-1])


def seq2route(seq):
    return [0] + list(seq) + [0]


def generate_time_info(seq1, seq2, seq1_time_info, seq2_time_info, tm):
    # time_info:
    #       0       1   2   3   4   5
    #   [time_len, es, ls, ef, lf, wait]
    ef1 = seq1_time_info[3] + tm[seq1, seq2]
    lf1 = seq1_time_info[4] + tm[seq1, seq2]
    # wait time between 1 and 2 = max{es2 - lf1, 0}
    wait = max(seq2_time_info[1] - lf1, 0)
    if wait == 0:
        # new_seq es = max{ef1, es2} - time_len1 - t12
        es = max(ef1, seq2_time_info[1]) - seq1_time_info[0] - tm[seq1, seq2]
        # new_seq ls = min{lf1, ls2} - time_len1 -t12
        ls = min(lf1, seq2_time_info[2]) - seq1_time_info[0] - tm[seq1, seq2]
    else:
        es = seq1_time_info[2]
        ls = seq1_time_info[2]
    # new_seq time_len = time_len1 + 30 + t12 + wait + time_len2
    time_len = seq1_time_info[0] + tm[seq1, seq2] + wait + seq2_time_info[0]
    # new_seq wait time
    wait += seq1_time_info[-1] + seq2_time_info[-1]
    return [time_len, es, ls, es + time_len, ls + time_len, wait]


def calculate_route_cost(seq, vehicle_type, wait, charge_cnt, ds, tm):
    cost = 0
    total_ds = ds[(0,), seq] + ds[seq, (0,)]
    total_tm = tm[(0,), seq] + tm[seq, (0,)]
    if len(seq) > 1:
        node1 = seq[:1]
        for node2 in seq[1:]:
            total_ds += ds[node1, (node2,)]
            total_tm += tm[node1, (node2,)]
            node1 = (node2,)
    cost += total_ds * (TRANS_COST_1 if vehicle_type == 1 else TRANS_COST_2)
    cost += FIXED_COST_1 if vehicle_type == 1 else FIXED_COST_2
    cost += wait * WAIT_COST
    cost += charge_cnt * CHARGE_COST
    return cost, total_ds, total_tm


def calculate_seq_distance(seq, ds):
    total_ds = 0
    if len(seq) > 1:
        node1 = seq[:1]
        for node2 in seq[1:]:
            total_ds += ds[node1, (node2,)]
            node1 = (node2,)
    return total_ds


def calculate_result_cost(seq, route_info):
    is_type_1 = True if route_info[0] else False
    cost = route_info[3] * (TRANS_COST_1 if is_type_1 else TRANS_COST_2)
    cost += FIXED_COST_1 if is_type_1 else FIXED_COST_2
    cost += route_info[5][-1] * WAIT_COST
    cost += route_info[6] * CHARGE_COST
    return cost


def check_merge_available(seq1, seq2, route_info1, route_info2, ds, tm, verbose=False):
    result = 0
    # vehicle type
    if route_info1[0] != route_info2[0]:
        result = 1
    # weight limit
    if route_info1[1] + route_info2[1] > (WEIGHT_1 if route_info1[0] == 1 else WEIGHT_2):
        result = 2
    # volume limit
    if route_info1[2] + route_info2[2] > (VOLUME_1 if route_info1[0] == 1 else VOLUME_2):
        result = 3
    # distance limit
    # if route_info1[6] + route_info2[6] >= 1:
    ds_limit = DISTANCE_1 if route_info1[0] == 1 else DISTANCE_2
    new_seq = (0,) + seq1 + seq2 + (0,)
    charge_index = [(i, v) for i, v in enumerate(new_seq) if v > 1000 or v == 0]
    i1, v1 = charge_index[0]
    for i2, v2 in charge_index[1:]:
        tmp_seq = new_seq[i1: i2+1]
        if calculate_seq_distance(tmp_seq, ds) > ds_limit:
            result = 4
            break
        i1, v1 = i2, v2
    # time limit
    if route_info1[5][4] + tm[seq1, seq2] >= route_info2[5][2]:
        result = 5
    if verbose:
        if result == 1:
            print("vehicle type is not same")
        elif result == 2:
            print("over weight limit")
        elif result == 3:
            print("over volume limit")
        elif result == 4:
            print("over distance limit")
        elif result == 5:
            print("over time window limit")
    return True if result == 0 else False


def delete_charge_end(seq, route_info, ds, tm):
    # seq = (n1, n2, ..., n3, c)
    if seq[-1] > 1000:
        new_seq = seq[:-1]
        ds_limit = DISTANCE_1 if route_info[0] == 1 else DISTANCE_2
        charge_index = [(i, v) for i, v in enumerate(new_seq) if v > 1000 or v == 0]
        if len(charge_index) != 0:
            i, v = charge_index[-1]
            last_seq = new_seq[i:]
        else:
            last_seq = new_seq
        if calculate_seq_distance((0,)+last_seq+(0,), ds) <= ds_limit:
            cost, total_ds, total_tm = calculate_route_cost(
                seq[:-1], route_info[0], route_info[5][-1], route_info[6] - 1, ds, tm
            )
            new_time_info = [
                route_info[5][0] - tm[seq[-2:-1], seq[-1:]] - 30,
                route_info[5][1],
                route_info[5][2],
                route_info[5][3] - tm[seq[-2:-1], seq[-1:]] - 30,
                route_info[5][4] - tm[seq[-2:-1], seq[-1:]] - 30,
                route_info[5][5]
            ]
            new_route_info = [
                route_info[0],
                route_info[1],
                route_info[2],
                total_ds,
                total_tm,
                new_time_info,
                route_info[6] - 1,
                cost
            ]
            return seq[:-1], new_route_info
    return seq, route_info


def save_result(route_dict, tm):
    csv_head = "trans_code,vehicle_type,dist_seq,distribute_lea_tm," \
               "distribute_arr_tm,distance,trans_cost,charge_cost," \
               "wait_cost,fixed_use_cost,total_cost,charge_cnt"
    with open("output/Result.csv", "w") as w:
        w.write(csv_head + "\n")

        for i, (seq, info) in enumerate(route_dict.items()):
            # seq: route_info[...]
            #   0 vehicle_type
            #   1 total_weight
            #   2 total_volume
            #   3 total_distance
            #   4 total_time
            #   5 time_info :       0       1   2   3   4   5
            #                   [time_len, es, ls, ef, lf, wait]
            #   6 charge_cnt
            #   7 cost
            trans_code = "DP%04d" % (i + 1)
            vehicle_type = str(info[0])
            dist_seq = ";".join([str(x) for x in seq2route(seq)])

            lea_tm = route_dict[seq][5][1] - tm[(0,), seq]
            arr_tm = route_dict[seq][5][3] + tm[(seq[0],), (0,)]
            if lea_tm < 0:
                arr_tm -= lea_tm
                lea_tm = 0
            distribute_lea_tm = num2time(lea_tm)
            distribute_arr_tm = num2time(arr_tm)

            distance = info[3]
            charge_cnt = info[6]
            charge_cost = charge_cnt * CHARGE_COST
            trans_cost = distance * (TRANS_COST_1 if info[0] == 1 else TRANS_COST_2)
            wait_cost = info[5][-1] * WAIT_COST
            fixed_use_cost = FIXED_COST_1 if info[0] == 1 else FIXED_COST_2
            total_cost = trans_cost + charge_cost + wait_cost + fixed_use_cost
            if total_cost != info[-1]:
                print("-" * 10)
                print(seq)
                print("old cost: " + str(info[-1]))
                print("total cost: " + str(total_cost))

            value = trans_code + "," + vehicle_type + "," + \
                    dist_seq + "," + distribute_lea_tm + "," + \
                    distribute_arr_tm + "," + str(distance) + "," + \
                    "%.2f" % trans_cost + "," + str(charge_cost) + "," + \
                    "%.2f" % wait_cost + "," + str(fixed_use_cost) + "," + \
                    "%.2f" % total_cost + "," + str(charge_cnt) + "\n"
            w.write(value)


def calculate_sequence_cost(seq, wait, vehicle_type, ds):
    cost = 0
    ds_len = ds[(0,), seq[:1]] + ds[seq[-1:], (0,)]

    if len(seq) > 1:
        node = seq[:1]
        for v in seq[1:]:
            ds_len += ds[node, (v,)]
            node = (v,)

    cost += ds_len * TRANS_COST_2 + FIXED_COST_2 \
        if vehicle_type == 2 \
        else ds_len * TRANS_COST_1 + FIXED_COST_1
    cost += wait * WAIT_COST

    return cost, ds_len


def num2time(n):
    return "%02d" % (n // 60 + 8) + ":" + "%02d" % (n % 60)


# def save(route_dict, tm, first):
#     csv_head = "trans_code,vehicle_type,dist_seq,distribute_lea_tm," \
#                "distribute_arr_tm,distance,trans_cost,charge_cost," \
#                "wait_cost,fixed_use_cost,total_cost,charge_cnt"
#     with open("output/Result.csv", "w") as w:
#         w.write(csv_head + "\n")
#
#         for i, (seq, info) in enumerate(route_dict.items()):
#             trans_code = "DP%04d" % (i + 1)
#             vehicle_type = str(info[0])
#             dist_seq = ";".join([str(x) for x in seq2route(seq)])
#
#             lea_tm = first[seq] - tm[(0,), seq]
#             arr_tm = first[seq] + info[4] + tm[(seq[0],), (0,)]
#             if lea_tm < 0:
#                 arr_tm -= lea_tm
#                 lea_tm = 0
#             distribute_lea_tm = num2time(lea_tm)
#             distribute_arr_tm = num2time(arr_tm)
#
#             distance = info[3]
#             charge_cnt = info[6]
#             charge_cost = charge_cnt * 50
#             trans_cost = distance * TRANS_COST_2 if info[0] == 2 else distance * TRANS_COST_1
#             wait_cost = info[5][-1] * WAIT_COST
#             fixed_use_cost = FIXED_COST_2 if info[0] == 2 else FIXED_COST_1
#             total_cost = trans_cost + charge_cost + wait_cost + fixed_use_cost
#
#             value = trans_code + "," + vehicle_type + "," + \
#                     dist_seq + "," + distribute_lea_tm + "," + \
#                     distribute_arr_tm + "," + str(distance) + "," + \
#                     "%.2f" % trans_cost + "," + str(charge_cost) + "," + \
#                     "%.2f" % wait_cost + "," + str(fixed_use_cost) + "," + \
#                     "%.2f" % total_cost + "," + str(charge_cnt) + "\n"
#             w.write(value)


class SeqDict(dict):

    def __getitem__(self, item):
        if len(item) != 2:
            return dict.__getitem__(self, item)
        else:
            a, b = item
            try:
                return dict.__getitem__(self, (a[-1:], b[:1]))
            except TypeError:
                raise BaseException("SeqDict TypeError in: " + str(item))
