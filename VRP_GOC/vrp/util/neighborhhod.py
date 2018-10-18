from vrp.common.model import SeqInfo

from functools import reduce
from typing import Tuple, Dict, List


def calculate_seq_position(
        seq: Tuple, position: Dict[Tuple, Tuple]
) -> Tuple:
    return reduce(
        lambda x, y: (x[0] + y[0], x[1] + y[1]),
        [position[x] for x in seq]
    )


def calculate_distance(
        seq1: Tuple, seq2: Tuple, position_dict: Dict[Tuple, Tuple]
) -> float:
    p1 = position_dict[seq1]
    p2 = position_dict[seq2]
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def get_neighborhood_dict(
        route_dict: Dict[Tuple, SeqInfo],
        position: Dict[Tuple, Tuple],
        neighborhood_number: int = 10
) -> Dict[Tuple, List[Tuple]]:
    """
    get neighborhoods of each route
    :param route_dict:
    :param position:
    :param neighborhood_number:
    :return:
    """
    seq_list = list(route_dict.keys())
    position_dict = {
        seq: calculate_seq_position(seq, position)
        for seq in seq_list
    }
    neighborhood_dict = dict()
    for seq in seq_list:
        compare_list = [
            (comp, calculate_distance(seq, comp, position_dict))
            for comp in seq_list if comp != seq
        ]
        compare_list.sort(key=lambda x: x[-1])
        neighborhood_dict[seq] = [
            x[0] for x in compare_list[:neighborhood_number]
        ]
    return neighborhood_dict
