import sympy as sy
from tools import sheet_read, plot, checks, tool
import pickle as pk
import re
import sympy.abc as syv  # import all variables
import os
from constants import m_e

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


# load and unpickle a PTKSession object
def load_session(path):
    with open(path, "rb") as file:
        s = pk.load(file)
        # s = PKTSession(path)
        s.path = path  # if "save_session_as" was used, self.path might be old
    return s


class PKTSession:
    """
    Session stores all functions, variables, vectors, constants and figures in dictionaries.
    The methods to access/manipulate the dicts often return a string with error/succes messages, so that an app can show the messages

    """
    def __init__(self, path):
        self.path = path
        self.funs = {}
        self.vars = {"x": syv.x, "y": syv.y, "z": syv.z}
        self.consts = {"m_e": m_e}
        self.vecs = {}
        self.figs = {}
        self._dicts = {
            "Functions":    self.funs,
            "Variables":    self.vars,
            "Constants":    self.consts,
            "Vectors":      self.vecs,
            "Plots":        self.figs,
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

    def check_fun_auto_add_var(self, fun, include_funs=True, include_constants=True):
        """
        Automatically adds a variable for strings in a function
        :param include_constants:   Also add variables for constants
        :param include_funs:        # TODO: Use functions in function declaration, eg. f=cos(x) and g=2*f(x)
        :param fun:                 str, function without "f="
        :return:                    str, output for status bar
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
        return f"Saved Variable {varname}"

    def add_vec(self, vecname: str, array):
        # better use add_vecs for string declarations
        self.vecs.update({vecname: array})
        return f"Saved Vector {vecname}"

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
            try:
                valid, array = tool.str_to_processed_arr(veclist[1], vecdict=self.vecs, dtype=dtype)
                if valid:
                    # only add if "replace=True" or not already existing
                    if replace or veclist[0] not in self.vecs:
                        self.vecs.update({veclist[0]: array})
                        output += f"added {veclist[0]},"
                    else:
                        output += f"NOT added: {veclist[0]} (already existing),"
                else:
                    output += f"NOT added: {vector.split('=')[0]} (invalid vector),"
            except IndexError:
                output += f"NOT added: {vector} (invalid expression),"
        return output.strip(",")

    def add_table(self, path, sep=","):
        self.vecs.update(sheet_read.get_vectors(sheet_read.read_table(path, sep=sep)))

    #
    # PLOT STUFF
    #
    def add_fig(self, figname: str, figsize=None, dpi=300, tight_layout=False, constrained_layout=False, axes=None):
        """
        Add the settings for a matplotlib figure, so that it can be created if needed
        :param axes:
        :param figname:
        :param figsize:
        :param dpi:
        :param tight_layout:
        :param constrained_layout:
        :return:
        """
        if axes is None:
            axes = {}
        d = {"figsize": figsize, "dpi": float(dpi), "tight_layout": tight_layout, "constrained_layout": constrained_layout, "axes": axes}
        if figname != "":
            self.figs.update({figname: d})
            return f"Added figure '{figname}'"
        return f"Invalid figure name: '{figname}'"

    def add_axes(self, figname, axname, title=None, xlabel=None, ylabel=None, legend=False, fontsize="13", grid="major", gline="-", gcolor="#777",
                 xlim=None, ylim=None, xscale="linear", yscale="linear", plots=None):
        """
        Add settings and data for a matplotlib axis, so that it can be created if needed
        :param plots:
        :param figname:
        :param axname:
        :param title:
        :param xlabel:
        :param ylabel:
        :param legend:
        :param fontsize:
        :param grid:
        :param gline:
        :param gcolor:
        :param xlim:
        :param ylim:
        :param xscale:
        :param yscale:
        :return:
        """
        if plots is None:
            plots = {}
        if figname in self.figs:
            if "axes" in self.figs[figname]:
                d = {"title": title, "xlabel": xlabel, "ylabel": ylabel, "legend": legend, "fontsize": fontsize, "grid": grid, "gline": gline, "gcolor": gcolor,
                     "xlim": xlim, "ylim": ylim, "xscale": xscale, "yscale": yscale, "plots": plots}
                self.figs[figname]["axes"].update({axname: d})
                return f"Added axes '{axname}' to figure '{figname}'"
            return f"figure '{figname}' has no 'axes' entry to add '{axname}'"
        return f"Invalid figure name: '{figname}'"

    def add_plot(self, figname, axname, plotname, xdata, ydata, marker=None, line="-", color=None, label=None):
        """
        Add settings and data for a matplotlib plot, so that it can be created if needed
        :param figname:
        :param axname:
        :param plotname:
        :param xdata:
        :param ydata:
        :param marker:
        :param line:
        :param color:
        :param label:
        :return:
        """
        if figname in self.figs and "axes" in self.figs[figname]:
            if axname in self.figs[figname]["axes"]:
                self.figs[figname]["axes"][axname]["plots"].update({plotname: {"xdata": xdata, "ydata": ydata, "marker": marker, "line": line, "color": color, "label": label}})
                return f"Added plot '{plotname}' to axes '{axname}' of figure '{figname}'"
            return f"Invalid axis name: '{axname}'"
        return f"Invalid figure name: '{figname}'"

    def create_fig(self, figname):
        """
        Create a matplotlib figure from the settings in self.figs
        :param figname:     str: dictionary key
        :return:            matplotlib figure object or Error
        """
        fig = None
        ax = None
        try:
            figsize = None
            if tool.str_to_list(self.figs[figname]["figsize"])[0]:
                figsize = tool.str_to_list(self.figs[figname]["figsize"])[1]
            for axes in self.figs[figname]["axes"]:
                ax_d = self.figs[figname]["axes"][axes]
                for pl in ax_d["plots"]:
                    """# get the arrays/data
                    if ax_d["plots"][pl]["xdata"] in self.vecs:
                        xdata = self.vecs[ax_d["plots"][pl]["xdata"]]
                    # check if its an array
                    elif tool.str_to_arr(ax_d["plots"][pl]["xdata"], float)[0]:
                        xdata = tool.str_to_arr(ax_d["plots"][pl]["xdata"], float)[1]
                    else:
                        raise TypeError("xdata is not in session vectors or array")
                    # get the arrays/data
                    if ax_d["plots"][pl]["ydata"] in self.vecs:
                        ydata = self.vecs[ax_d["plots"][pl]["xdata"]]
                    # check if its an array
                    elif tool.str_to_arr(ax_d["plots"][pl]["ydata"], float)[0]:
                        ydata = tool.str_to_arr(ax_d["plots"][pl]["ydata"], float)[1]
                    else:
                        raise TypeError("ydata is not in session vectors or array")"""
                    xvalid, xdata = tool.str_to_processed_arr(ax_d["plots"][pl]["xdata"], vecdict=self.vecs)
                    if not xvalid:
                        raise TypeError(f"Invalid xdata: '{ax_d['plots'][pl]['xdata']}'")
                    yvalid, ydata = tool.str_to_processed_arr(ax_d["plots"][pl]["ydata"], vecdict=self.vecs)
                    if not yvalid:
                        raise TypeError(f"Invalid ydata: '{ax_d['plots'][pl]['ydata']}'")

                    fig, ax = plot.plot(xdata, ydata, marker=ax_d["plots"][pl]["marker"],
                                        line=ax_d["plots"][pl]["line"], color=ax_d["plots"][pl]["color"], label=ax_d["plots"][pl]["label"],       # line options
                                        fig=fig, ax=ax, dpi=self.figs[figname]["dpi"], figsize=figsize,                                        # figure/axes options todo:tight/constrained_layout
                                        title=ax_d["title"], xlabel=ax_d["xlabel"], ylabel=ax_d["ylabel"], legend=ax_d["legend"], fontsize=ax_d["fontsize"],  # labels....
                                        grid=ax_d["grid"], gline=ax_d["gline"], gcolor=ax_d["gcolor"],
                                        xlim=ax_d["xlim"], ylim=ax_d["ylim"], xscale=ax_d["xscale"], yscale=ax_d["yscale"],                                  # axes options
                                        show=False)
        except TypeError as ex:
            return ex
        except KeyError as ex:
            return ex
        return fig

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
        if re.fullmatch(r"[a-zA-ZüÜöÖäÄ_\- ]+\.ptk", filename):  # check if entered filename is valid and has extension
            filename_valid = True
        elif re.fullmatch(r"[a-zA-ZüÜöÖäÄ_\- ]+", filename):  # check if entered filename is valid but does not have extension
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
        """
        for SAVE Session Saving use check_save_session
        :param path:
        :return:
        """
        with open(path, "wb") as file:
            pk.dump(self, file)

    def save_session(self):
        """
        for SAVE Session Saving use check_save_session
        :return:
        """
        with open(self.path, "wb") as file:
            pk.dump(self, file)

    def __repr__(self):
        return f"funs:{self.funs} vars:{self.vars} vecs:{self.vecs} plots:{self.figs}"
