from vrp.common.model import *

from itertools import *
from functools import reduce


seq = (1, 2, 3)
tm = SeqDict({
    x: y
    for x, y in zip(zip(zip((0, 1, 2, 3)), zip((1, 2, 3, 0))), (40, 20, 20, 10))
})
first = {
    x: y
    for x, y in zip(zip(range(4)), (0, 60, 150, 180))
}
last = {
    x: y
    for x, y in zip(zip(range(4)), (960, 120, 180, 210))
}

tuple_seq = tuple(zip((0, *seq, 0)))
tm_edge = tuple(map(
    lambda x, y: tm[x] + y,
    zip(tuple_seq[:-1], tuple_seq[1:]),
    chain((0,), repeat(30))
))


def _eps_reduce(x, y):
    r = max(x[0] + y[0], y[1])
    x[1].append(r)
    return r, x[1]


_, el = reduce(_eps_reduce, chain(
    [(0, list())], zip(tm_edge, (first[x] for x in tuple_seq[1:]))
))
delta = tuple(map(
    lambda n1, n2, t12: max(first[n2] - first[n1] - t12, 0),
    tuple_seq[:-1], tuple_seq[1:], tm_edge
))
reversed_delta = (0,) + tuple(accumulate(reversed(delta)))
eps_list = list(map(
    lambda x, y: x+y,
    (0, *el), reversed(reversed_delta)
))


def _lps_reduce(x, y):
    r = min(x[0] - y[0], y[1])
    x[1].append(r)
    return r, x[1]


_, ll = reduce(
    _lps_reduce, chain(
        [(960, list())],
        zip(reversed(tm_edge), (last[x] for x in reversed(tuple_seq[:-1])))
    )
)
