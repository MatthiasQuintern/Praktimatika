import re
from tools import checks
import numpy as np


def str_to_processed_arr(arrstring: str, arrdict=None, dtype=float):
    """
    Gets a string and returns a float or numpy array. The string can contain numpy array slicing
    :param dtype:       data type of np array
    :param arrstring:   name of the array in vecdict or like this [1, 2.5, .9, 5][0:3:2]
    :param arrdict:     dictionary, which should contain the array name as key if vecstring is a name
    :return:            bool: success, float/np.ndarray
    """
    arrstring = arrstring.replace(" ", "")
    vec = None
    # check if its a number
    match = re.search("^(" + checks.NUMBER + "|(-?inf))", arrstring)
    if match:
        if checks.is_number(match.group()):
            vec = float(match.group())
    else:
        # get the array from string
        match = re.search(r"^\[" + checks.NUMBER +"(," + checks.NUMBER +")*]", arrstring)
        if match:
            valid, vec = str_to_arr(match.group(), dtype=dtype)
        # get the array from vecdict
        elif isinstance(arrdict, dict):
            match = re.search("^" + checks.NAME, arrstring)
            if match:
                print(match, match.group())
                if match.group() in arrdict:
                    vec = arrdict[match.group()]

    # check if there are any opertaions performed on vec recursively
    if vec is not None:
        reststring = arrstring.replace(match.group(), "")

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
            # slice the array
            vec = vec[slc[0]:slc[1]:slc[2]]
            reststring = reststring.replace(match.group(), "")
        if len(reststring) > 0:
            # check for *+-/
            if reststring[0] == "*":
                valid, restvec = str_to_processed_arr(reststring[1:], arrdict=arrdict, dtype=dtype)
                if valid:
                    vec *= restvec
            elif reststring[0] == "+":
                valid, restvec = str_to_processed_arr(reststring[1:], arrdict=arrdict, dtype=dtype)
                if valid:
                    vec += restvec
            elif reststring[0] == "-":
                valid, restvec = str_to_processed_arr(reststring[1:], arrdict=arrdict, dtype=dtype)
                if valid:
                    vec -= restvec
            elif reststring[0] == "/":
                valid, restvec = str_to_processed_arr(reststring[1:], arrdict=arrdict, dtype=dtype)
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


