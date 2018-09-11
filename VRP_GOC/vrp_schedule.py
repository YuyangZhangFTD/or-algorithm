from vrp_constant import *


def schedule_time(seq, param):
    """
    schedule a sequence
    :param seq:
    :param param:
    :return:
    """
    _, tm, _, _, first, last, _, _ = param
    node1 = (0,)
    serve_time = 0
    eps = 0         # early possible starting
    lps = 960       # latest possible starting
    total_wait = 0
    total_shift = 0
    total_delta = 0
    time_len = 0
    for i in range(len(seq)):
        node2 = seq[i:i + 1]

        if node1 == node2:
            return None, None, None, None, None, None

        shift = max(0, lps + tm[node1, node2] + serve_time - last[node2])

        # lps = lps_node2
        if shift > 0:
            lps = last[node2]
            total_shift += shift
        else:
            lps += tm[node1, node2] + serve_time

        # check: if lps_node1 < eps_node1, return None
        if lps - tm[node1, node2] - serve_time < eps:
            return None, None, None, None, None, None

        # update wait and lps_node2
        wait = max(0, first[node2] - lps)
        if wait > 0:
            total_wait += wait
            lps = max(first[node2], lps)

        # eps = eps_node2
        total_delta += max(0,
                           first[node2] - eps - serve_time - tm[node1, node2])
        eps = max(eps + serve_time + tm[node1, node2], first[node2])

        # time_len += tm + serve + wait
        time_len += tm[node1, node2] + serve_time + wait

        # iter
        serve_time = SERVE_TIME
        node1 = node2

    time_len += SERVE_TIME + tm[node1, (0,)]  # back to depot

    es = 0 + total_delta - total_wait
    ls = 960 - total_shift
    ef = es + time_len
    lf = ls + time_len
    return time_len, es, ls, ef, lf, total_wait
