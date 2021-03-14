from tools import sheet_read, plot, checks, tool
import pickle as pk
import re
import sympy as sy
import sympy.abc as syv  # import all variables
import os


# load and unpickle a PTKSession object
def load_session(path):
    with open(path, "rb") as file:
        s = pk.load(file)
        # s = PKTSession(path)
        s.path = path  # if "save_session_as" was used, self.path might be old
    return s


class PKTSession:
    """
    Session stores all functions, variables, arrays, constants and figures in dictionaries.
    The methods to access/manipulate the dicts often return a string with error/succes messages, so that an app can show the messages

    """
    def __init__(self, path):
        self.path = path
        self.funs = {}
        self.vars = {"x": syv.x, "y": syv.y, "z": syv.z}
        try:
            from constants import const_d
        except ImportError:
            const_d = {}
        self.consts = const_d

        self.arrs = {}
        self.figs = {}
        self._dicts = {
            "Functions":    self.funs,
            "Variables":    self.vars,
            "Constants":    self.consts,
            "Arrays":       self.arrs,
            # Legacy
            "Vectors":      self.arrs,
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
            if not string in self.vars and not string in checks.FUNCTIONS and (string not in self.funs or not include_funs) and (string not in self.consts or not include_constants):
                self.add_var(string)
                output += f"added var: {string},"
        return output

    def add_var(self, varname: str):
        self.vars.update({varname: sy.symbols(varname)})
        return f"Saved Variable {varname}"

    def add_arr(self, arrname: str, array):
        # better use add_arrs for string declarations
        self.arrs.update({arrname: array})
        return f"Saved Array {arrname}"

    def add_arrs(self, arrs: iter, replace=True, dtype=float):
        """
        :param dtype:       data type
        :param replace:     boolean wether to replace functions with conflicting names
        :param arrs:        iterable with strings in this form: "v=[4, 2, 2.5]"
        :return:            str, output for status bar
        """
        output = ""
        for array in arrs:
            arrlist = array.replace(" ", "").split("=")
            try:
                valid, array = tool.str_to_processed_arr(arrlist[1], arrdict=self.arrs, dtype=dtype)
                if valid:
                    # only add if "replace=True" or not already existing
                    if replace or arrlist[0] not in self.arrs:
                        self.arrs.update({arrlist[0]: array})
                        output += f"added {arrlist[0]},"
                    else:
                        output += f"NOT added: {arrlist[0]} (already existing),"
                else:
                    output += f"NOT added: {array.split('=')[0]} (invalid array),"
            except IndexError:
                output += f"NOT added: {array} (invalid expression),"
        return output.strip(",")

    def add_table(self, path, sep=","):
        self.arrs.update(sheet_read.get_arrays(sheet_read.read_table(path, sep=sep)))

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
                    xvalid, xdata = tool.str_to_processed_arr(ax_d["plots"][pl]["xdata"], arrdict=self.arrs)
                    if not xvalid:
                        raise TypeError(f"Invalid xdata: '{ax_d['plots'][pl]['xdata']}'")
                    yvalid, ydata = tool.str_to_processed_arr(ax_d["plots"][pl]["ydata"], arrdict=self.arrs)
                    if not yvalid:
                        raise TypeError(f"Invalid ydata: '{ax_d['plots'][pl]['ydata']}'")

                    fig, ax = plot.plot(xdata, ydata, marker=ax_d["plots"][pl]["marker"],
                                        line=ax_d["plots"][pl]["line"], color=ax_d["plots"][pl]["color"], label=ax_d["plots"][pl]["label"],       # line options
                                        fig=fig, dpi=self.figs[figname]["dpi"], figsize=figsize, fontsize=ax_d["fontsize"],
                                        constrained_layout=self.figs[figname]["constrained_layout"], tight_layout=self.figs[figname]["tight_layout"],
                                        ax=ax, title=ax_d["title"], xlabel=ax_d["xlabel"], ylabel=ax_d["ylabel"], legend=ax_d["legend"],   # axes options
                                        xlim=ax_d["xlim"], ylim=ax_d["ylim"], xscale=ax_d["xscale"], yscale=ax_d["yscale"],
                                        grid=ax_d["grid"], gline=ax_d["gline"], gcolor=ax_d["gcolor"],
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
            status = f"Invalid filename '{filename}'. Name must only contain: 'a-zA-ZüÜäÄöÖ_- '"

        if os.path.isdir(path):  # check if entered path is valid dir
            if not re.fullmatch(".+/$", path):  # check if "/" is at the end of the directory
                path += "/"
            path_valid = True
            if not os.access(path, os.W_OK):  # Check for write access
                path_valid = False
                status = f"Invalid directory '{path}'. Not enough permission to write in directory"
        elif os.path.isfile(path):  # check if entered path is a file
            status = f"Invalid directory '{path}'. Directory is a file. Please remove the filename from the path."

        if filename_valid and path_valid:
            if isinstance(self, PKTSession):
                self.save_session_as(path + filename)  # call the save_as method from the session
                status = "PKT-Session saved successfully."
            else:
                status = "Error: No session is loaded."

        elif path == "" and filename == "":
            if isinstance(self, PKTSession):
                if os.access(self.path, os.W_OK) and os.path.isfile(self.path):  # check for write access and if path is a file
                    self.save_session()  # save the session with the internal path
                    status = "PKT-Session saved successfully."
                else:
                    status = "Invalid Path: PKT-Session contains invalid path no other was given."
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
        return f"funs:{self.funs} vars:{self.vars} arrs:{self.arrs} plots:{self.figs}"
