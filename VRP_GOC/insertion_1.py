from typing import *

from vrp_reader import read_data, get_node_info
from vrp_structure import SeqInfo
from vrp_util import generate_seq_info
from vrp_check import check_merge_seqs_available
from vrp_constant import *

data_set_num = 5
select_pair_num = 20

ds, tm, delivery, pickup, charge, node_type_judgement = read_data(data_set_num)
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


seq_candidate = {*delivery, *pickup}

