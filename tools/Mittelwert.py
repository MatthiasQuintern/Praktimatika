import numpy as np
import sympy as sy


def weighted_median(vals, uncerts):
    weights = 1 / (uncerts ** 2)

    weight_sum = np.sum(weights)

    median = np.dot(vals, weights)/weight_sum  # sum(v_i*w_i): np.dot(v, w)

    u_inner = np.sqrt(1/weight_sum)
    u_external = np.sqrt(np.dot(weights, (median - vals)**2) / ((len(vals) - 1) * weight_sum))

    return median, u_inner, u_external


print(weighted_median(np.array([200.5, 199.9]), np.array([2.7, 2.6])))
