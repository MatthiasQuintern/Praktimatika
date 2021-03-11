import re
from tools import checks
import numpy as np


def str_to_processed_arr(vecstring: str, vecdict=None, dtype=float):
    """
    Gets a string and returns a float or numpy array. The string can contain numpy array slicing
    :param dtype:       data type of np array
    :param vecstring:   name of the vector in vecdict or like this [1, 2.5, .9, 5][0:3:2]
    :param vecdict:     dictionary, which should contain the vector name as key if vecstring is a name
    :return:            bool: success, float/np.ndarray
    """
    vecstring = vecstring.replace(" ", "")
    vec = None
    # check if its a number
    match = re.search("^("+checks.NUMBER+"|(-?inf))", vecstring)
    if match:
        if checks.is_number(match.group()):
            vec = float(match.group())
    else:
        # get the array from string
        match = re.search(r"^\["+checks.NUMBER+"(,"+checks.NUMBER+")*]", vecstring)
        if match:
            valid, vec = str_to_arr(match.group(), dtype=dtype)
        # get the array from vecdict
        elif isinstance(vecdict, dict):
            match = re.search("^" + checks.NAME, vecstring)
            if match:
                print(match, match.group())
                if match.group() in vecdict:
                    vec = vecdict[match.group()]

    # check if there are any opertaions performed on vec recursively
    if vec is not None:
        reststring = vecstring.replace(match.group(), "")

        # test for slice
        match = re.search(r"^\[.+]", reststring)
        if match and isinstance(vec, np.ndarray):
            # assume it is a slice, since otherwise it is invalid syntax
            slcs = match.group().strip("[]").split(":")
            slc = [0, None, 1]
            for i in range(len(slcs)):
                if i > 2:
                    break
                elif checks.is_int(slcs[i]):
                    slc[i] = int(slcs[i])
            # slice the vector
            vec = vec[slc[0]:slc[1]:slc[2]]
            reststring = reststring.replace(match.group(), "")
        if len(reststring) > 0:
            # check for *+-/
            if reststring[0] == "*":
                valid, restvec = str_to_processed_arr(reststring[1:], vecdict=vecdict, dtype=dtype)
                if valid:
                    vec *= restvec
            elif reststring[0] == "+":
                valid, restvec = str_to_processed_arr(reststring[1:], vecdict=vecdict, dtype=dtype)
                if valid:
                    vec += restvec
            elif reststring[0] == "-":
                valid, restvec = str_to_processed_arr(reststring[1:], vecdict=vecdict, dtype=dtype)
                if valid:
                    vec -= restvec
            elif reststring[0] == "/":
                valid, restvec = str_to_processed_arr(reststring[1:], vecdict=vecdict, dtype=dtype)
                if valid:
                    vec /= restvec
        return True, vec
    return False, None


def str_to_arr(s: str, dtype=float):
    """
    Turns a string with into a nparry. Values must be separated with ,
    :param s:       string like "[4, 5., .04] or (4.3, 2, 5, 9)
    :param dtype:   data type
    :return:        bool: success, array/None
    """
    s = s.strip("[]() \n")
    arr = s.split(",")
    try:
        return True, np.array(arr, dtype=dtype)
    except ValueError:
        return False, None


def str_to_list(s: str, length=None):
    """
    Turns a string with into a nparry. Values must be separated with ,
    :param s:       string like "[4, 5., .04] or (4.3, 2, 5, 9)
    :param length:  int: length of the array
    :return:        bool: success, array/None
    """
    s = s.strip("[]() \n")
    l = s.split(",")
    if length:
        if not len(l) == length:
            return False, None
    return True, l


v = np.array([1, 2.6, 3, 4, 5, 6, .7, 8])
w = np.array([1, 2.60, 13, -46, 5, 36.55, .709, 1])
d = {"ve": v, "w_69": w}
print(str_to_processed_arr("w_69*ve/2", vecdict=d))


def get_p0_bounds(order, values_dict):
    """
    returns a p0 list and a bounds list
    :param order:
    :param values_dict:      {"x": "pmin, pmax, p0", "y": "..."}
    :return:            [p0s], [pmins], [pmaxs]
    """
    p0 = []
    pmin = []
    pmax = []
    if not len(order) == len(values_dict):
        return None, None, None
    for i in range(len(values_dict)):
        valid, ls = str_to_list(values_dict[order[i]], length=3)
        if valid:
            p0.append(ls[0])
            pmin.append(ls[0])
            pmax.append(ls[0])
        else:
            return None, None, None
    return p0, pmin, pmax


def get_max_vec_length(vecs):
    max_l = 0
    for vec in vecs:
        if isinstance(vec, np.ndarray):
            if max_l < vec.shape[0]:
                max_l = vec.shape[0]
        else:
            if max_l < len(vec):
                max_l = len(vec)
    return max_l


