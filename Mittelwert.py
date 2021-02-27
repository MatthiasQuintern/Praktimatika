import numpy as np
import sympy as sy


def weighted_median(vals, uncerts):
    weights = 1 / (uncerts ** 2)

    weight_sum = np.sum(weights)

    median = np.dot(vals, weights)/weight_sum  # sum(v_i*w_i): np.dot(v, w)

    u_inner = np.sqrt(1/weight_sum)
    u_external = np.sqrt(np.dot(weights, (median - vals)**2) / ((len(vals) - 1) * weight_sum))

    return median, u_inner, u_external


@np.vectorize
def calc(f, x):
    return f.subs(x).evalf()
"""
value = np.array((1, 1, 1, 2))
uncertainties = np.array((1, 1, 1, 2))

print(weighted_median(value, uncertainties))

"""

