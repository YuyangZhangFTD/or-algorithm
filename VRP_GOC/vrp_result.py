from vrp_structure import SeqInfo
from vrp_cost import calculate_each_cost


def num2time(n):
    return "%02d" % (n // 60 + 8) + ":" + "%02d" % (n % 60)


def save_result(route_dict, num):
    csv_head = "trans_code,vehicle_type,dist_seq,distribute_lea_tm," \
               "distribute_arr_tm,distance,trans_cost,charge_cost," \
               "wait_cost,fixed_use_cost,total_cost,charge_cnt"
    with open("output/Result" + str(num) + ".csv", "w") as w:
        w.write(csv_head + "\n")

        info: SeqInfo
        for i, (seq, info) in enumerate(route_dict.items()):
            trans_code = "DP%04d" % (i + 1)
            vehicle_type = info.vehicle_type
            dist_seq = ";".join([str(x) for x in (0,) + seq + (0,)])

            distribute_lea_tm = num2time(info.ls)
            distribute_arr_tm = num2time(info.lf)

            distance = info.total_distance
            charge_cnt = info.charge_cnt
            wait = info.wait
            trans_cost, fixed_use_cost, wait_cost, charge_cost = calculate_each_cost(
                distance, vehicle_type, wait, charge_cnt
            )
            total_cost = info.cost
            value = trans_code + "," + str(vehicle_type) + "," + \
                    dist_seq + "," + distribute_lea_tm + "," + \
                    distribute_arr_tm + "," + str(distance) + "," + \
                    "%.2f" % trans_cost + "," + str(charge_cost) + "," + \
                    "%.2f" % wait_cost + "," + str(fixed_use_cost) + "," + \
                    "%.2f" % total_cost + "," + str(charge_cnt) + "\n"
            w.write(value)
