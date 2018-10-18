from vrp.common.constant import *


def calculate_each_cost(distance, vehicle_type, wait, charge_cnt):
    is_type_1 = True if vehicle_type == 1 else False
    trans_cost = distance * (TRANS_COST_1 if is_type_1 else TRANS_COST_2)
    fixed_cost = FIXED_COST_1 if is_type_1 else FIXED_COST_2
    wait_cost = WAIT_COST * wait
    charge_cost = charge_cnt * CHARGE_COST
    return trans_cost, fixed_cost, wait_cost, charge_cost


def calculate_info_cost(info):
    return calculate_each_cost(
        info.total_distance,
        info.vehicle_type,
        info.wait,
        info.charge_cnt
    )
