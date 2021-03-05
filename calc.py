import sympy as sy
import re
import numpy as np
from scipy.optimize import curve_fit


# geht wahrscheinlich irgendwie besser
@np.vectorize   # unnecessary?
def calculate(f, values: dict):
    fun = get_py_fun(f, values.keys())
    return fun(*values.values())


def get_py_fun(f, variables):
    """
    returns a python function with variables as args
    f="cos(x)+z"
    variables = ["x", "z"]
    -> function(x, z): return np.cos(x)+z
    :param f:           function: str/sympy function
    :param variables:   list with variable names as string
    :return:            python function (sympy lambdify function)
    """
    return np.vectorize(sy.lambdify(variables, f, "numpy"))


def get_needed_values(f):
    output = []
    f = str(f)
    variables = re.findall(r"[a-zA-Z]+[a-zA-Z0-9_]*", f)
    for var in variables:
        if var not in FUNCTIONS:
            output.append(var)
    return output


def fit(f, x, y, p0=None):
    params, covarmatrix = curve_fit(f, x, y, p0=p0)
"""    popt: array
    Optimal
    values
    for the parameters so that the sum of the squared
    residuals
    of
    ``f(xdata, *popt) - ydata`` is minimized.
    pcov: 2 - D
    array
    The
    estimated
    covariance
    of
    popt.The
    diagonals
    provide
    the
    variance
    of
    the
    parameter
    estimate.To
    compute
    one
    standard
    deviation
    errors
    on
    the
    parameters
    use
    ``perr = np.sqrt(np.diag(pcov))
    ``."""

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

f = sy.sympify("exp(4*z)")
x = np.array([5, 9, 3])
z = np.array([34, 5, 6])
print("calc:", calculate(f, {"z": 5}))
fun = sy.sympify("tan(x+5*z)-10")
vecs = {"x": np.array([3, 5, 9]), "z": np.array([1, 2, 4])}
vals = {"x": 10, "z": 4}
print(calculate(fun, vals))
