from vrp.io.result import read_solution, save_result
from vrp.io.reader import read_data, get_node_info
from vrp.util.info import generate_seq_info
from vrp.util.neighborhhod import get_neighborhood_dict
from vrp.improvement import two_opt, two_opt_star
from vrp.common.model import Param

from random import choice

data_set_num = 1
iter_number = 100000

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

new_cost = 0
old_cost = 0
final_route_dict = dict()

for seq in route_dict:
    info = generate_seq_info(seq, param)
    route_dict[seq] = info
neighborhood_dict = get_neighborhood_dict(
    route_dict, position, neighborhood_number=10
)

# ===================================================================
candidate_seqs = list(route_dict)
have_updated = False
for _ in range(iter_number):

    if have_updated:
        candidate_seqs = list(route_dict)
        neighborhood_dict = get_neighborhood_dict(
            route_dict, position, neighborhood_number=10
        )
    seq = choice(candidate_seqs)
    neighborhood = choice(neighborhood_dict[seq])
    (new_seq1, new_info1), (new_seq2, new_info2) = two_opt_star(
        seq, route_dict[seq],
        neighborhood, route_dict[neighborhood],
        param, iter_num=15
    )
    if new_seq1 != seq and new_seq2 != neighborhood:
        print("="*30)
        have_updated = True
        i1 = route_dict.pop(seq)
        route_dict[new_seq1] = new_info1
        i2 = route_dict.pop(neighborhood)
        route_dict[new_seq2] = new_info2
        print(seq)
        print(i1)
        print(neighborhood)
        print(i2)
        print("---")
        print(new_seq1)
        print(new_info1)
        print(new_seq2)
        print(new_info2)
        print("---")
        print("old cost: " + str(i1.cost + i2.cost))
        print("new cost: " + str(new_info1.cost + new_info2.cost))

cost = 0
for k, v in route_dict.items():
    print("-"*30)
    print(k)
    print(v)
    new_seq, new_info = two_opt(k, v, param, best_accept=True)
    print(new_seq)
    print(new_info)
    final_route_dict[new_seq] = new_info
    cost += new_info.cost

print("-"*20+"\nnew cost: " + str(cost))
save_result(final_route_dict, data_set_num)
