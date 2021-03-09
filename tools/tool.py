import re
import checks
import numpy as np


def str_to_sliced_arr(vecstring: str, vecdict=None, dtype=float):
    """
    Gets a string and returns a float or numpy array. The string can contain numpy array slicing
    :param dtype:       data type of np array
    :param vecstring:   name of the vector in vecdict or like this [1, 2.5, .9, 5][0:3:2]
    :param vecdict:     dictionary, which should contain the vector name as key if vecstring is a name
    :return:            bool: success, float/np.ndarray
    """
    vecstring = vecstring.replace(" ", "")
    # check if the vec string is...
    # ...number
    if checks.is_number(vecstring):
        return True, float(vecstring)

    vec = None
    # get the array from string
    match = re.search(r"^\[[\d.]+", vecstring)
    if match:
        vec = str_to_arr(match.group(), dtype=dtype)
    # get the array from vecdict
    elif isinstance(vecdict, dict):
        match = re.search("^"+checks.NAME, vecstring)
        if match:
            print(match, match.group())
            if match.group() in vecdict:
                vec = vecdict[match.group()]
    if vec is not None:
        if isinstance(vec, np.ndarray):
            # assume there is a slice afterwards
            slcs = vecstring.replace(match.group(), "").strip("[]").split(":")
            slc = [0, -1, 1]
            for i in range(len(slcs)):
                if i > 2:
                    break
                elif checks.is_int(slcs[i]):
                    slc[i] = int(slcs[i])
            # return the sliced vector
            return True, vec[slc[0]:slc[1]:slc[2]]
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
        return True, nparray(arr, dtype=dtype)
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
d = {"ve": v}
print(str_to_sliced_arr("ve", vecdict=d))


