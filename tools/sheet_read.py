import numpy as np
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
            from pandas import read_excel
            return read_excel(path, keep_default_na=False, header=None).values.tolist()
        except FileNotFoundError as ex:
            print(ex)
            return [[]]
        except ImportError as ex:
            print(ex)
            return [[]]
    else:
        try:
            return read_csv(path, sep=sep)
        except FileNotFoundError as ex:
            print(ex)
            return [[]]

    # return read_excel(path, keep_default_na=False).values.tolist()  # if keep_default_na is true, empty cells are 'nan' and not None


# legacy
def get_vectors(lis):
    return get_arrays(list)


def get_arrays(lis):
    """
    :param lis:    list with lines, each line is list with cells
    :returns:       dictionary containing numpy arrays with string as key
    """
    # iterates over every element, if element is string look for numbers below the element
    vectors = {}
    for i in range(len(lis)):
        for j in range(len(lis[i])):
            # csv[i][j] is the name of the array, if it can not be interpreted as a number it can be a valid array name
            try:
                float(lis[i][j])
            except ValueError:
                if lis[i][j] != "":     # empty string is not a valid array name
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
