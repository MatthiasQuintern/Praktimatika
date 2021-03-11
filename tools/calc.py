import sympy as sy
import re
import numpy as np
from scipy.optimize import curve_fit


# from https://docs.sympy.org/latest/modules/functions/index.html
FUNCTIONS = ['re', 'im', 'sign', 'Abs', 'arg', 'conjugate', 'polar_lift', 'periodic_argument', 'principal_branch',
             #'sympy.functions.elementary.trigonometric',
             # 'TrigonometricFunctions',
             'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'sinc',
             # 'TrigonometricInverses',
             'asin', 'acos', 'atan', 'acot', 'asec', 'acsc', 'atan2',
             # 'sympy.functions.elementary.hyperbolic', 'HyperbolicFunctions',
             'HyperbolicFunction', 'sinh', 'cosh', 'tanh', 'coth', 'sech', 'csch',
             #'HyperbolicInverses',
             'asinh', 'acosh', 'atanh', 'acoth', 'asech', 'acsch',
             # 'sympy.functions.elementary.integers',
             'ceiling', 'floor', 'RoundFunction', 'frac',
             # 'sympy.functions.elementary.exponential',
             'exp', 'LambertW', 'log', 'exp_polar',
             # 'sympy.functions.elementary.piecewise',
             'ExprCondPair', 'Piecewise',
             # 'sympy.functions.elementary.miscellaneous',
             'IdentityFunction', 'Min', 'Max', 'root', 'sqrt', 'cbrt', 'real_root', 'Combinatorial', 'bell', 'bernoulli', 'binomial', 'catalan', 'euler', 'factorial', 'subfactorial', 'factorial2/doublefactorial', 'FallingFactorial', 'fibonacci', 'tribonacci', 'harmonic', 'lucas', 'genocchi', 'partition', 'MultiFactorial', 'RisingFactorial', 'stirling',
             # 'Enumeration',
             'nC', 'nP', 'nT',
             # 'Special',
             'DiracDelta', 'Heaviside', 'SingularityFunction',
             # 'Gamma,BetaandrelatedFunctions',
             'ErrorFunctionsandFresnelIntegrals',
             # 'Exponential,LogarithmicandTrigonometricIntegrals',
             'BesselTypeFunctions', 'AiryFunctions', 'B-Splines', 'RiemannZetaandRelatedFunctions', 'HypergeometricFunctions', 'Ellipticintegrals', 'MathieuFunctions', 'OrthogonalPolynomials', 'SphericalHarmonics', 'TensorFunctions']


def calculate(f, values: dict):
    fun = get_py_fun(f, values.keys())
    return fun(*values.values())


def get_py_fun(f, variables, vectorize=True):
    """
    returns a python function with variables as args
    f="cos(x)+z"
    variables = ["x", "z"]
    -> function(x, z): return np.cos(x)+z
    :param vectorize:   wether the function should be np.vectorized
    :param f:           function: str/sympy function
    :param variables:   list with variable names as string
    :return:            python function (sympy lambdify function)
    """
    if vectorize:
        return np.vectorize(sy.lambdify(variables, f, "numpy"))
    return sy.lambdify(variables, f, "numpy")


def get_needed_values(f):
    """
    returns a list with the values needed to evaluate a function
    :param f:
    :return:
    """
    output = []
    f = str(f)
    variables = re.findall(r"[a-zA-Z]+[a-zA-Z0-9_]*", f)
    for var in variables:
        if var not in FUNCTIONS and var not in output:
            output.append(var)
    return output


def fit(f, x, y, p0=None, bounds=(-np.inf, np.inf)):
    params, covarmatrix = curve_fit(f, x, y, p0=p0, bounds=bounds)
    return params, covarmatrix


def str_fit(f, x, y, variable="x", ret_uncerts=True, p0=None, bounds=(-np.inf, np.inf)):
    """
    Fits a function to x-y dataset. Function can  be string or sympy function
    Returns a sympy function with all fit parameters inserted
    :param ret_uncerts: wether to return uncertainty array or the pcov matrix
    :param f:           str or sympy function
    :param x:           x-data (array)
    :param y:           y-data (array)
    :param variable:    the variable in the function which is NOT a fit parameter
    :param p0:          dictionary starting values for the fitparameters
    :param bounds:      dictionary bound for the fitparameters
    :return:            (sympy function, params, pcov)
    """
    # TODO: p0, bounds
    variables = get_needed_values(f)
    # put the NOT fit parameter at first list pos, since scipy curve_fit treats the first arg as the variable and the rest as parameters
    variables.insert(0, variables.pop(variables.index(variable)))

    # get the python function from f
    pyfun = get_py_fun(f, variables, vectorize=False)
    # get fit paramteres and pcov
    params, pcov = fit(pyfun, x, y, p0=p0, bounds=bounds)
    # Get a new sympy function, with all paramters inserted
    f = sy.sympify(f)
    f = f.subs([(variables[i+1], params[i]) for i in range(len(params))])
    if ret_uncerts:
        return f, params, uncerts_from_pcov(pcov)
    return f, params, pcov


def uncerts_from_pcov(pcov):
    return np.sqrt(np.diag(pcov))



