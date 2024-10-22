import sympy as sy


def error_propagation(f: sy.Function, variables):
    """
    returns the error propagation formula of f in respect to the variables
    err = sqrt(sum((df/dv*u(v))**2))
    :param f:           sympy function
    :param variables:   iter: variables to consider as sympy Symbols
    :return:            sympy function
    """
    g = 0
    for var in variables:
        if not isinstance(var, sy.Symbol):
            if isinstance(var, str):
                var = sy.Symbol(var)
        df = f.diff(var) * sy.Symbol(f"u{var}")
        g = df ** 2 + g

    return sy.sqrt(g)

