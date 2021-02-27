import numpy as np
from pandas import read_excel
import re


def read_csv(path, sep=','):
    """
    :param path:    path to a csv-like file
    :param sep:     the seperator of the values in the csv
    :returns:       list containing all lines, where each line is a list with all values.
    """
    output = []
    with open(path, "r") as csv:
        for line in csv:
            output.append(line.replace("\n", "").split(sep=sep))
    return output


def read_table(path, sep=","):
    """
    :param path:    absolute or relative (to this file) path to the file containing the table
    :param sep:     seperator
    :return:        list with lines, each line is list with cells
    """
    if re.fullmatch(r".*\.(xls|xlsx|xlsm|xlsb|odf|ods|odt)$", path):    # all pandas.read_excel supported filetypes
        try:
            return read_excel(path, keep_default_na=False).values.tolist()
        except FileNotFoundError as ex:
            print(ex)
            return [[]]
    else:
        try:
            return read_csv(path, sep=sep)
        except FileNotFoundError as ex:
            print(ex)
            return [[]]

    # return read_excel(path, keep_default_na=False).values.tolist()  # if keep_default_na is true, empty cells are 'nan' and not None


def get_vectors(lis):
    """
    :param lis:    list with lines, each line is list with cells
    :returns:       dictionary containing numpy arrays with string as key
    """
    # iterates over every element, if element is string look for numbers below the element
    vectors = {}
    for i in range(len(lis)):
        for j in range(len(lis[i])):
            # csv[i][j] is the name of the vector, if it can not be interpreted as a number it can be a valid vector name
            try:
                float(lis[i][j])
            except ValueError:
                if lis[i][j] != "":     # empty string is not a valid vector name
                    vec = []
                    done = False
                    k = i + 1
                    while not done:
                        if k == len(lis):
                            done = True
                            continue
                        try:
                            val = float(lis[k][j])
                            vec.append(val)
                        except TypeError:
                            done = True
                        except ValueError:
                            done = True
                        finally:
                            k += 1
                    if len(vec) > 0:
                        vectors.update({lis[i][j]: np.array(vec)})

    return vectors

"""test = [
    ["a", "b", "c", "d"],
    [1,    1,   0,   5],
    ["e",  2,   5,   None],
    [69,  3,   None, None]
]"""

# enumerate try: except: else: finally:
# @np.vectorize -> beliebige function auf np.arrays anwendbar machen
# csv = read_csv("Isotherme.csv")
# print(csv)
# vecs = get_vectors(csv)
# print(vecs)
# f or name, vec in vecs.items():
#    print(f"{name}:\tlength {len(vec)}")

