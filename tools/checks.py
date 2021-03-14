"""
Methods to check if a argument passes certain criteria.
"""

import re
import os
from numpy import array as nparray

# from https://docs.sympy.org/latest/modules/functions/index.html
FUNCTIONS = ['re', 'im', 'sign', 'Abs', 'arg', 'conjugate', 'polar_lift', 'periodic_argument', 'principal_branch',
             # 'sympy.functions.elementary.trigonometric',
             # 'TrigonometricFunctions',
             'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'sinc',
             # 'TrigonometricInverses',
             'asin', 'acos', 'atan', 'acot', 'asec', 'acsc', 'atan2',
             # 'sympy.functions.elementary.hyperbolic', 'HyperbolicFunctions',
             'HyperbolicFunction', 'sinh', 'cosh', 'tanh', 'coth', 'sech', 'csch',
             # 'HyperbolicInverses',
             'asinh', 'acosh', 'atanh', 'acoth', 'asech', 'acsch',
             # 'sympy.functions.elementary.integers',
             'ceiling', 'floor', 'RoundFunction', 'frac',
             # 'sympy.functions.elementary.exponential',
             'exp', 'LambertW', 'log', 'exp_polar',
             # 'sympy.functions.elementary.piecewise',
             'ExprCondPair', 'Piecewise',
             # 'sympy.functions.elementary.miscellaneous',
             'IdentityFunction', 'Min', 'Max', 'root', 'sqrt', 'cbrt', 'real_root', 'Combinatorial', 'bell', 'bernoulli', 'binomial', 'catalan', 'euler', 'factorial',
             'subfactorial', 'factorial2/doublefactorial', 'FallingFactorial', 'fibonacci', 'tribonacci', 'harmonic', 'lucas', 'genocchi', 'partition', 'MultiFactorial',
             'RisingFactorial', 'stirling',
             # 'Enumeration',
             'nC', 'nP', 'nT',
             # 'Special',
             'DiracDelta', 'Heaviside', 'SingularityFunction', 'Gamma,BetaandrelatedFunctions', 'ErrorFunctionsandFresnelIntegrals',
             'Exponential,LogarithmicandTrigonometricIntegrals', 'BesselTypeFunctions', 'AiryFunctions', 'B-Splines', 'RiemannZetaandRelatedFunctions', 'HypergeometricFunctions',
             'Ellipticintegrals', 'MathieuFunctions', 'OrthogonalPolynomials', 'SphericalHarmonics', 'TensorFunctions']

# REGEX PATTERNS
NUMBER = r"((([0-9]+.[0-9]*)|\.[0-9]+)([eE]-?\d+)?)"
NAME = r"([a-zA-Z][a-zA-Z0-9]*(_[a-zA-Z0-9]*)*)"
DEF_FUNS = "((re)|(im)|(sign)|(Abs)|(arg)|(conjugate)|(polar_lift)|(periodic_argument)|(principal_branch)|(sin)|(cos)|(tan)|(cot)|(sec)|(csc)|(sinc)|(asin)|(acos)|(atan)|(acot)|(asec)|(acsc)|(atan2)|(HyperbolicFunction)|(sinh)|(cosh)|(tanh)|(coth)|(sech)|(csch)|(asinh)|(acosh)|(atanh)|(acoth)|(asech)|(acsch)|(ceiling)|(floor)|(RoundFunction)|(frac)|(exp)|(LambertW)|(log)|(exp_polar)|(ExprCondPair)|(Piecewise)|(IdentityFunction)|(Min)|(Max)|(root)|(sqrt)|(cbrt)|(real_root)|(Combinatorial)|(bell)|(bernoulli)|(binomial)|(catalan)|(euler)|(factorial)|(subfactorial)|(factorial2)|(doublefactorial)|(FallingFactorial)|(fibonacci)|(tribonacci)|(harmonic)|(lucas)|(genocchi)|(partition)|(MultiFactorial)|(RisingFactorial)|(stirling)|(nC)|(nP)|(nT)|(DiracDelta)|(Heaviside)|(SingularityFunction)|(ErrorFunctionsandFresnelIntegrals)|(BesselTypeFunctions)|(AiryFunctions)|(B-Splines)|(RiemannZetaandRelatedFunctions)|(HypergeometricFunctions)|(Ellipticintegrals)|(MathieuFunctions)|(OrthogonalPolynomials)|(SphericalHarmonics)|(TensorFunctions))"
VALID = f"({NAME}|({DEF_FUNS}?"+r"\(\)))"
VALID_F = VALID+r"(([+\-*/]|\*\*)"+VALID+")*"


def is_readable_file(path):
    """
    Checks wether the 'path' is a file and if it can be read
    :param path:    path to the file
    :return:        (bool: readable, str: status)
    """
    valid = True
    status = "File can be read"
    if not os.path.isfile(path):
        valid = False
        status = "Invalid filepath: Not a file."
    if not os.access(path, os.R_OK):
        valid = False
        status = "Invalid filepath: No read acces for file."
    return valid, status


def is_valid_fun(function: str):
    function = function.replace(" ", "")
    if not function.count("=") == 1:
        return False, "Missing '=' or more than one '='"
    name, f = function.split("=")
    if not re.fullmatch(NAME, name):
        return False, f"Invalid name: {name}"
    res = is_valid_subfun(f)
    if not res[0]:
        return False, res[1]
    return True, "Valid"


def is_valid_subfun(f: str):
    # opening / closung paranthesis count must be equal
    print(f)
    f = f.replace(" ", "")
    if not f.count("(") == f.count(")"):
        return False, "Invalid Function: Unequal opening/closing paranthesis count"

    outer = ""          # the string without arguments in paranthesis
    open_index = 0      # stores the indices of the opening paranthesis
    open_count = 0
    close_count = 0
    # check if all substrings inside paranthesis are valid subfuns recursively
    for i in range(len(f)):
        print(open_count, close_count, outer)
        if f[i] == "(":
            if open_count == 0:
                outer += "("
                open_index = i
            open_count += 1

        elif f[i] == ")":
            close_count += 1
            # check if a paranthesis was opened before
            if open_count == 0:
                return False, "Closing Paranthesis before one is opened"
            # if at most outer yet opened paranthesis
            if open_count == close_count:
                # check if the substring between the () is a valid function
                sub_res = is_valid_subfun(f[open_index+1:i])
                if not sub_res[0]:
                    return False, sub_res[1]
                open_count = close_count = 0

        if open_count == 0:
            outer += f[i]

    # string before "(" must be known function, nothing or *+-**/
    if not re.fullmatch(VALID_F, outer):
        return False, "Invalid characters, variable names, function names or shape"

    return True, "Valid"


def is_name_list(l: str):
    """
    checks if the string consists of names separated by a whitespace
    :param l:
    :return:
    """
    try:
        if re.fullmatch("([a-zA-Z0-9_]+ )*([a-zA-Z0-9_]+)?", l):
            return True
    except TypeError:
        pass
    return False


def is_number_array(arr):
    try:
        nparray(arr, dtype=float)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def is_number(num: str, allow_inf=True):
    if is_float(num, allow_inf=allow_inf):
        return True
    elif is_int(num):
        return True
    return False


def is_float(num: str, allow_inf=True):
    add = ""
    if allow_inf:
        add = "|(-?inf)"
    try:
        if re.fullmatch(NUMBER + add, num):
            return True
    except TypeError:
        pass
    return False


def is_int(num: str):
    try:
        if re.fullmatch("[0-9]+", num):
            return True
    except TypeError:
        pass
    return False


def is_name(name: str):
    """
    eg, sA93Asl_9A9a, but not 9a, a__a
    Allowed characters: a-zA-Z0-9_
    """
    try:
        if re.fullmatch(NAME, name):
            return True
    except TypeError:
        pass
    return False





