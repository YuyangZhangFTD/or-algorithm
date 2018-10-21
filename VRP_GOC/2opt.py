from vrp.io.result import read_solution, save_result
from vrp.util.info import generate_seq_info
from vrp.io.reader import read_data, get_node_info
from vrp.improvement.intra_route import two_opt
from vrp.common.model import Param

data_set_num = 5
route_dict = read_solution(data_set_num)

ds, tm, delivery, pickup, charge, position, ntj = read_data(data_set_num)
delivery = get_node_info(delivery)
pickup = get_node_info(pickup)
charge = get_node_info(charge, is_charge=True)
node_id_d, volume_d, weight_d, first_d, last_d = delivery
node_id_p, volume_p, weight_p, first_p, last_p = pickup
node_id_c, _, _, first_c, last_c = charge

volume = {**volume_d, **volume_p}
del volume_d, volume_p
weight = {**weight_d, **weight_p}
del weight_d, weight_p
first = {**first_d, **first_p, **first_c}
del first_d, first_p, first_c
last = {**last_d, **last_p, **last_c}
del last_d, last_p, last_c

first[(0,)] = 0
last[(0,)] = 960

param = Param(ds, tm, volume, weight, first, last, ntj, position)


cost = 0
final_route_dict = dict()
for seq in route_dict:
    info = generate_seq_info(
        seq, param
    )
    if len(seq) == 1:
        continue
    new_seq, new_info = two_opt(
        seq, info, param, best_accept=True
    )
    if new_info:
        print("-"*20)
        print(seq)
        print(info)
        print(new_seq)
        print(new_info)
        final_route_dict[new_seq] = new_info
        cost += new_info.cost
    else:
        final_route_dict[seq] = info
        cost += info.cost

print("final cost: " + str(cost))
save_result(final_route_dict, data_set_num)
