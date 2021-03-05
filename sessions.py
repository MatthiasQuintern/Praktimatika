import sympy as sy
from tools import sheet_read
import pickle as pk
import re
import sympy.abc as syv    # import all variables
import os
from constants import m_e
import checks
import numpy as np
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
             'DiracDelta', 'Heaviside', 'SingularityFunction', 'Gamma,BetaandrelatedFunctions', 'ErrorFunctionsandFresnelIntegrals', 'Exponential,LogarithmicandTrigonometricIntegrals', 'BesselTypeFunctions', 'AiryFunctions', 'B-Splines', 'RiemannZetaandRelatedFunctions', 'HypergeometricFunctions', 'Ellipticintegrals', 'MathieuFunctions', 'OrthogonalPolynomials', 'SphericalHarmonics', 'TensorFunctions']


# load and unpickle a PTKSession object
def load_session(path):
    with open(path, "rb") as file:
        s = pk.load(file)
        # s = PKTSession(path)
        s.path = path   # if "save_session_as" was used, self.path might be old
    return s


class PKTSession:
    def __init__(self, path):
        self.path = path
        self.funs = {}
        self.vars = {"x": syv.x, "y": syv.y, "z": syv.z}
        self.consts = {"m_e": m_e}
        self.vecs = {}
        self.plots = {}
        self._dicts = {
                        "Functions": self.funs,
                        "Variables": self.vars,
                        "Constants": self.consts,
                        "Vectors":   self.vecs,
                        "Plots":     self.vecs,
                       }

    #
    # OUTPUTTING STUFF
    #
    def list_dict(self, dictionary: str, only_name=True):
        if dictionary in self._dicts:
            output = f"{dictionary}:"
            if only_name:
                for entryname in self._dicts[dictionary].keys():
                    output += entryname + ", "
            else:
                output += "\n"
                for entryname, entry in self._dicts[dictionary].items():
                    output += f"\t{entryname}={entry}\n"
            return output

        else:
            return f"invalid dictionary: {dictionary}. valid are {[d for d in self._dicts.keys()]}"

    def get_dict(self, dictionary: str, only_name=False):
        if dictionary in self._dicts:
            output = []
            if only_name:
                for entryname in self._dicts[dictionary].keys():
                    output.append(entryname)
            else:
                for entryname, entry in self._dicts[dictionary].items():
                    output.append(f"{entryname}={entry}")
            return output

        else:
            return f"invalid dictionary: {dictionary}. valid are {[d for d in self._dicts.keys()]}"

    #
    # ADDING STUFF
    #
    def add_funs(self, funs: iter, replace=True, auto_vars=True):
        """
        :param auto_vars:   boolean wether to automatically add variables from the function
        :param replace:     boolean wether to replace functions with conflicting names
        :param funs:        iterable with strings in this form: "f=cos(x)+y**(exp(5))"
        :return:            str, output for status bar
        """
        output = ""
        for function in funs:
            if checks.is_valid_fun(function):
                funlist = function.replace(" ", "").split("=")
                # only add if "replace=True" or not already existing
                if replace or funlist[0] not in self.funs:
                    self.funs.update({funlist[0]: sy.sympify(funlist[1], evaluate=False)})
                    output += f"added {funlist[0]},"
                    if auto_vars:
                        output += self.check_fun_auto_add_var(funlist[1])
                else:
                    output += f"NOT added: {funlist[0]} (already existing),"
            else:
                output += f"NOT added: {function.split('=')[0]} (invalid function),"
        return output.strip(",")

    def add_vecs(self, vecs: iter, replace=True, dtype=float):
        """
        :param dtype:       data type
        :param replace:     boolean wether to replace functions with conflicting names
        :param vecs:        iterable with strings in this form: "v=[4, 2, 2.5]"
        :return:            str, output for status bar
        """
        output = ""
        for vector in vecs:
            veclist = vector.replace(" ", "").split("=")
            valid, array = checks.str_to_arr(veclist[1], dtype=dtype)
            if valid:
                # only add if "replace=True" or not already existing
                if replace or veclist[0] not in self.vecs:
                    self.vecs.update({veclist[0]: array})
                    output += f"added {veclist[0]},"
                else:
                    output += f"NOT added: {veclist[0]} (already existing),"
            else:
                output += f"NOT added: {vector.split('=')[0]} (invalid vector),"
        return output.strip(",")


    def check_fun_auto_add_var(self, fun, include_funs=True, include_constants=True):
        """
        Automatically adds a variable for strings in a function
        :param fun: str, function without "f="
        :return:    str, output for status bar
        """
        output = ""
        strings = re.findall(r"[a-zA-Z]+[a-zA-Z0-9_]*", fun)
        for string in strings:
            if not string in self.vars and not string in FUNCTIONS and (string not in self.funs or not include_funs) and (string not in self.consts or not include_constants):
                self.add_var(string)
                output += f"added var: {string},"
        return output

    def add_var(self, varname: str):
        self.vars.update({varname: sy.symbols(varname)})
        return "Savec Variable"

    def add_vec(self, vecname: str, array):
        self.vecs.update({vecname: array})
        return "Saved Vector"

    def add_table(self, path, sep=","):
        self.vecs.update(sheet_read.get_vectors(sheet_read.read_table(path, sep=sep)))

    #
    # SAVING SESSIONS with python pickle
    #
    def check_save_session(self, path="", filename=""):
        """
        Saves the session and returns a status bar. if path AND filename are empty, session will be saved at session.path
        :param self:     PKTSession object
        :param path:        path to a .ptk file or a directory
        :param filename:    will be the filename if path is directory
        :return:            a string for a status bar
        """
        filename_valid = False
        path_valid = False
        status = "None"
        if re.fullmatch("[a-zA-ZüÜöÖäÄ_\- ]+\.ptk", filename):  # check if entered filename is valid and has extension
            filename_valid = True
        elif re.fullmatch("[a-zA-ZüÜöÖäÄ_\- ]+", filename):  # check if entered filename is valid but does not have extension
            filename += ".ptk"
            filename_valid = True
        else:
            status = "Invalid filename. Name must only contain: 'a-zA-ZüÜäÄöÖ_- '"

        if os.path.isdir(path):  # check if entered path is valid dir
            if not re.fullmatch(".+/$", path):  # check if "/" is at the end of the directory
                path += "/"
            path_valid = True
            if not os.access(path, os.W_OK):  # Check for write access
                path_valid = False
                status = "Invalid directory: Not enough permission to write in directory"
        elif os.path.isfile(path):  # check if entered path is a file
            status = "Invalid directory: directory is a file. Please remove the filename from the path."

        if filename_valid and path_valid:
            if isinstance(self, PKTSession):
                self.save_session_as(path + filename)  # call the save_as method from the session
                status = "PKTSession saved successfully."
            else:
                status = "Error: No session is loaded."

        elif path == "" and filename == "":
            if isinstance(self, PKTSession):
                if os.access(self.path, os.W_OK) and os.path.isfile(self.path):  # check for write access and if path is a file
                    self.save_session()  # save the session with the internal path
                    status = "PKTSession saved successfully."
                else:
                    status = "Invalid Path: PKTSession contains invalid path no other was given."
            else:
                status = "Error: No session is loaded."
        return status

    def save_session_as(self, path):
        with open(path, "wb") as file:
            pk.dump(self, file)

    def save_session(self):
        with open(self.path, "wb") as file:
            pk.dump(self, file)

    def __repr__(self):
        return f"funs:{self.funs} vars:{self.vars} vecs:{self.vecs} plots:{self.plots}"
