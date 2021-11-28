# encoding: utf-8

import itertools

from pysle.utilities import errors


def validateOption(variableName: str, value: str, optionClass) -> None:
    if value not in optionClass.validOptions:
        raise errors.WrongOption(variableName, value, optionClass.validOptions)


# The LCS code doesn't look like the rest of the code
# -- I'm guessing I copied or adapted the code from
#    someplace online
def _lcs_lens(xs: list, ys: list) -> list:
    curr = list(itertools.repeat(0, 1 + len(ys)))
    for x in xs:
        prev = list(curr)
        for i, y in enumerate(ys):
            if x == y:
                curr[i + 1] = prev[i] + 1
            else:
                curr[i + 1] = max(curr[i], prev[i + 1])
    return curr


def _lcs(xs: list, ys: list) -> list:
    nx, ny = len(xs), len(ys)
    if nx == 0:
        return []

    if nx == 1:
        return [xs[0]] if xs[0] in ys else []

    i = nx // 2
    xb, xe = xs[:i], xs[i:]
    ll_b = _lcs_lens(xb, ys)
    ll_e = _lcs_lens(xe[::-1], ys[::-1])
    _, k = max((ll_b[j] + ll_e[ny - j], j) for j in range(ny + 1))
    yb, ye = ys[:k], ys[k:]
    return _lcs(xb, yb) + _lcs(xe, ye)
