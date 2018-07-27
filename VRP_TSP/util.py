import numpy as np

TRANS_COST_1 = 12 / 1000
TRANS_COST_2 = 14 / 1000
FIXED_COST_1 = 200
FIXED_COST_2 = 300
WAIT_COST_PER_MIN = 24 / 60


def route2seq(route):
    return tuple(route[1:-1])


def seq2route(seq):
    return [0] + list(seq) + [0]


def sort_sequence_tw(sequence, first, last):
    seq = [
        (node, (first[node], last[node]))
        for node in sequence[1:-1]
    ]
    seq.sort(key=lambda x: x[1])
    return seq


def arrange_time(f1, l1, f2, l2, t12, time_len=30):
    first_1to2 = f1 + time_len + t12
    last_1to2 = l1 + time_len + t12
    wait = 0
    if last_1to2 <= f2:  # A-1
        es = l1
        ls = es
        ef = f2 + time_len
        lf = ef
        wait += f2 - last_1to2
    elif first_1to2 <= f2 <= last_1to2 <= l2:  # A-2 and A-3
        es = f2 - time_len - t12
        ls = l1
        ef = f2 + time_len
        lf = last_1to2 + time_len
    elif f1 <= f2 <= first_1to2 and last_1to2 < l2:  # A-4
        es = f1
        ls = l1
        ef = first_1to2 + time_len
        lf = last_1to2 + time_len
    elif first_1to2 <= f2 and l2 <= last_1to2:  # A-5, A-6 and A-8
        es = f2 - time_len - t12
        ls = l2 - time_len - t12
        ef = f2 + time_len
        lf = l2 + time_len
    elif f1 <= f2 <= first_1to2 <= l2 <= last_1to2:  # A-7 and A-9f3
        es = f1
        ls = l2 - time_len - t12
        ef = first_1to2 + time_len
        lf = l2 + time_len
    else:
        raise BaseException("wrong cases in A")

    return [es, ls, ef, lf, wait]


def calculate_sequence_cost(seq, wait, vehicle_type, ds):
    cost = 0
    ds_len = ds[(0,), (seq[0],)] + ds[(seq[-1],), (0,)]

    if len(seq) > 1:
        node = (seq[0],)
        for v in seq[1:]:
            ds_len += ds[node, (v,)]
            node = (v,)

    cost += ds_len * TRANS_COST_2 + FIXED_COST_2 \
        if vehicle_type == 2 \
        else ds_len * TRANS_COST_1 + FIXED_COST_1
    cost += wait * WAIT_COST_PER_MIN

    return cost, ds_len


def num2time(n):
    return "%02d" % (n // 60 + 8) + ":" + str(n % 60)


def save(route_dict, tm, first):
    csv_head = "trans_code,vehicle_type,dist_seq,distribute_lea_tm," \
               "distribute_arr_tm,distance,trans_cost,charge_cost," \
               "wait_cost,fixed_use_cost,total_cost,charge_cnt"
    with open("output/Result.csv", "w") as w:
        w.write(csv_head + "\n")

        for i, (seq, info) in enumerate(route_dict.items()):
            trans_code = "DP%04d" % (i + 1)
            vehicle_type = str(info[0])
            dist_seq = ";".join([str(x) for x in seq2route(seq)])
            distribute_lea_tm = num2time(first[seq] - tm[(0,), seq])
            distribute_arr_tm = num2time(first[seq] + info[4] + tm[(seq[0], ), (0,)])
            distance = info[3]
            charge_cnt = info[7]
            charge_cost = charge_cnt * 50
            trans_cost = distance * TRANS_COST_2 if info[0] == 2 else distance * TRANS_COST_1
            wait_cost = info[5][-1] * WAIT_COST_PER_MIN
            fixed_use_cost = FIXED_COST_1 if info[0] == 2 else FIXED_COST_2
            total_cost = trans_cost + charge_cost + wait_cost + fixed_use_cost

            value = trans_code + "," + vehicle_type + "," + \
                    dist_seq + "," + distribute_lea_tm + "," + \
                    distribute_arr_tm + "," + "%.2f" % distance + "," + \
                    "%.2f" % trans_cost + "," + str(charge_cost) + "," + \
                    "%.2f" % wait_cost + "," + str(fixed_use_cost) + "," + \
                    "%.2f" % total_cost + "," + str(charge_cnt) + "\n"
            w.write(value)
