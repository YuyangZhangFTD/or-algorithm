from vrp.common.model import SeqInfo
from vrp.evaluator.cost import calculate_each_cost

from typing import Dict, Tuple


def num2time(n):
    return "%02d" % (n // 60 + 8) + ":" + "%02d" % (n % 60)


def save_result(route_dict: Dict[Tuple, SeqInfo], num):
    csv_head = "trans_code,vehicle_type,dist_seq,distribute_lea_tm," \
               "distribute_arr_tm,distance,trans_cost,charge_cost," \
               "wait_cost,fixed_use_cost,total_cost,charge_cnt"
    with open("output/Result_" + str(num) + "_300.csv", "w") as w:
        w.write(csv_head + "\n")

        info: SeqInfo
        for i, (seq, info) in enumerate(route_dict.items()):
            trans_code = "DP%04d" % (i + 1)
            vehicle_type = info.vehicle_type
            dist_seq = ";".join([str(x) for x in (0,) + seq + (0,)])

            distribute_lea_tm = num2time(info.lps_list[0])
            distribute_arr_tm = num2time(info.lps_list[-1])

            distance = info.total_distance
            charge_cnt = sum(info.charge_index)
            wait = info.wait
            trans_cost, fixed_use_cost, wait_cost, charge_cost = \
                calculate_each_cost(distance, vehicle_type, wait, charge_cnt)
            total_cost = info.cost
            value = trans_code + "," + str(vehicle_type) + "," + \
                    dist_seq + "," + distribute_lea_tm + "," + \
                    distribute_arr_tm + "," + str(distance) + "," + \
                    "%.2f" % trans_cost + "," + str(charge_cost) + "," + \
                    "%.2f" % wait_cost + "," + str(fixed_use_cost) + "," + \
                    "%.2f" % total_cost + "," + str(charge_cnt) + "\n"
            w.write(value)


def read_solution(data_set_num):
    file_name = "solution/Result_" + str(data_set_num) + "_300.csv"
    route_dict = dict()
    with open(file_name) as f:
        f.readline()
        while True:
            s = f.readline()
            if len(s) < 1:
                break
            seq = tuple([int(x) for x in s.split(",")[2].split(";")[1:-1]])
            route_dict[seq] = None

    return route_dict
