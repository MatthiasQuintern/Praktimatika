import npyscreen as nps
import numpy as np
import sympy as sy
from tools import checks, tool, calc as cl, calc
from tui import tui_widgets as twid
from maths import error


#
# FUNCTION MENU
#
class UserFuncMenu(twid.BaseForm):
    DEFAULT_LINES = 20
    DEFAULT_COLUMNS = 90
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.FixedText, rely=1, relx=3, value="Select the action to perform on the function:")
        self.fun = self.add(nps.FixedText, rely=2, relx=3, value="None")
        self.options = self.add(twid.UserFuncAction, rely=5, relx=3)

        # self.status = self.add(nps.FixedText, rely=self.lines - 3, relx=3, value="")
        # self.status.important = True  # makes it bold and green

    def pre_edit_loop(self):
        self.fun.value = f"{self.parentApp.function[0]}={self.parentApp.function[1]}"
        self.fun.update()


class UserFuncCalc2(twid.BaseForm):
    """
    lets the user input the values/vectors to calculate a function
    the function is used is the parentApp.function, which is selected
    """
    DEFAULT_LINES = 40
    DEFAULT_COLUMNS = 120
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.cycle_widgets = True

        self.title = self.add(nps.FixedText, editable=False, rely=1, relx=3, value="Select the values to calculate the function")
        self.fun = self.add(nps.FixedText, editable=False, rely=2, relx=3, value="Function")
        self.vars = {}
        y1 = self.create_val_input(3, 3)

        self.b_calc = self.add(nps.ButtonPress, rely=y1 + 1, relx=1, name="Calculate", when_pressed_function=self.calc)
        self.result = self.add(nps.FixedText, rely=y1 + 2, relx=3, value="Result:")
        self.result_val = None     # store the value of the result, so that it can be processed
        self.res_name = self.add(nps.TitleText, rely=y1 + 3, relx=3, use_two_lines=False, name="Result name:", value="res")
        self.b_store_res = self.add(nps.ButtonPress, rely=y1 + 4, relx=1, name="Store Result as Vector", when_pressed_function=self.save_res)
        self.b_back = self.add(nps.ButtonPress, rely=y1 + 5, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        # status bar
        self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="Use 'Tab' key for autocompletion. Array slicing is supported.")
        self.status.important = True  # makes it bold and green

    def create_val_input(self, y, col):
        """
        create the value input widgets and return the position of the last widget
        """
        varlist = cl.get_needed_values(self.parentApp.function[1])

        for i in range(len(varlist)):
            value = ""
            # check if the varname is a constant or already defined array
            if varlist[i] in self.parentApp.ses.consts.keys():
                value = self.parentApp.ses.consts[varlist[i]]
            elif varlist[i] in self.parentApp.ses.arrs.keys():
                value = self.parentApp.ses.arrs[varlist[i]]
            # value must be string, otherwise there can be unfixable TypeError with 1-element numpy arrays
            self.vars.update({varlist[i]: self.add(twid.TArrSelect, rely=y + i, relx=col, name=f"{varlist[i]}:", value=str(value))})
        return len(self.vars) + y

    def _clear_all_widgets(self, ):
        self._widgets__ = []
        self._widgets_by_id = {}
        self._next_w_id = 0
        self.nextrely = self.DEFAULT_NEXTRELY
        self.nextrelx = self.DEFAULT_X_OFFSET
        self.editw = 0  # Index of widget to edit.

    def pre_edit_loop(self):
        """
        updates the vectornames and vectors widgets
        detects, which values are needed to calculate the function
        """
        # Remove all widgets and recreate them without variable widgets
        self._clear_all_widgets()
        self.create()

        self.fun.value = f"{self.parentApp.function[0]}={self.parentApp.function[1]}"
        self.fun.update()
        # set cursor to first var
        self.editw = 0

    def calc(self):
        d = {}  # dict with varname: array pairs
        for name, wid in self.vars.items():
            """ # IF THE CHECKS DON'T PASS, THE INPUT VALUE IS STILL INVALID/NONE!
            value = wid.value
            if str(value) in self.parentApp.ses.arrs:
                value = self.parentApp.ses.arrs[str(value)]
            # check if value is an array with numbers
            elif checks.is_number(value):
                value = float(value)
            # check if value is a number
            # elif checks.is_number_array(value):
            #     value = np.array(value, dtype=float)
            else:
                value = tool.str_to_arr(str(value))[1]
                # nps.notify_confirm(f"Can not convert {value} to a number or array")"""
            value = wid.get_arr()
            if value is not None:
                d.update({name: value})
            else:
                self.status.value = f"Invalid input for variable '{name}'"
        try:
            self.result_val = cl.calculate(self.parentApp.function[1], d)
            self.result.value = f"Result: {self.result_val}"
        except TypeError as ex:
            self.parentApp.output(ex)
        self.result.update()

    def save_res(self):
        if (checks.is_number(self.result_val) or checks.is_number_array(self.result_val)) and self.res_name.value != "":
            self.parentApp.ses.add_arr(self.res_name.value, np.array(self.result_val))
        else:
            nps.notify_confirm("Could not save array!")


class ErrorPropagation(twid.BaseForm):
    """
    Calculates the Error Propagation Function of a function
    """
    DEFAULT_LINES = 25
    DEFAULT_COLUMNS = 120
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.cycle_widgets = True
        y0 = 4
        y1 = y0 + 4
        self.desc = self.add(nps.MultiLine, editable=False, rely=2, relx=3, max_height=2,
                             values=["Calculates the error propagation formula of f in respect to the given variables:",
                                     "err = sqrt(sum((df/dv*u(v))**2))"])
        self.line0 = self.add(nps.FixedText, rely=y0, relx=3, editable=False, value="\u2501" * 200)
        self.fun = self.add(nps.FixedText, editable=False, rely=y0 + 1, relx=3, value="Function")
        self.desc = self.add(nps.FixedText, rely=y0+2, relx=3, editable=False, value="Enter the variables separated by a space character, eg: 'x y z'")
        self.vars = self.add(twid.Input, rely=y0 + 3, relx=3, name="Variables", check_method=checks.is_name_list)

        self.line1 = self.add(nps.FixedText, rely=y1, relx=3, editable=False, value="\u2501" * 200)
        self.b_calc = self.add(nps.ButtonPress, rely=y1 + 1, relx=1, name="Calculate Function", when_pressed_function=self.get_fun)
        self.err = self.add(nps.FixedText, rely=y1 + 2, relx=3, editable=False, value="Result:")
        self.err_fun = None     # store the sympy function so that it can be processed
        self.err_name = self.add(twid.Input, rely=y1 + 3, relx=3, use_two_lines=False, name="Function name:", value="err", check_method=checks.is_name)
        self.b_store_res = self.add(nps.ButtonPress, rely=y1 + 4, relx=1, name="Save Function", when_pressed_function=self.save_res)
        self.b_calc_err = self.add(nps.ButtonPress, rely=y1 + 5, relx=1, name="Calculate Error with values", when_pressed_function=self.save_res)
        self.b_back = self.add(nps.ButtonPress, rely=y1 + 6, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)

        # status bar
        self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="")
        self.status.important = True  # makes it bold and green

    def pre_edit_loop(self):
        """
        get the function from the session
        """
        self.fun.value = f"{self.parentApp.function[0]}={self.parentApp.function[1]}"
        self.fun.update()

    def get_fun(self):
        variables = self.vars.value.strip(" ").split(" ")
        for i in range(len(variables)):
            variables[i] = sy.Symbol(variables[i])
        self.err_fun = error.error_propagation(self.parentApp.function[1], variables)
        self.err.value = f"Result: {self.err_fun}"
        self.err.update()

    def save_res(self):
        if self.err_fun and self.err_name.valid_input:
            self.parentApp.ses.add_funs([f"{self.err_name.value}={self.err_fun}"])
        else:
            nps.notify_confirm("Could not save function! Either the function is invalid or name is empty")

    def calc_res(self):
        if self.err_fun and self.err_name.valid_input:
            self.parentApp.function = [self.err_name, self.err]
            self.parentApp.switchForm("m_fun_calc")
        else:
            nps.notify_confirm("Could not process function! Either the function is invalid or name is empty")


class CurveFit(twid.BaseForm):
    """
    lets the user curve-fit data with the function
    user must select xdata, ydata and "x" variable (the one that is NOT a parameter)
    """
    # DEFAULT_LINES = 25
    # DEFAULT_COLUMNS = 120
    # SHOW_ATX = 8
    # SHOW_ATY = 2

    def create(self):
        y0 = 1
        y1 = y0 + 2
        col1 = 3
        col2 = 35
        self.cycle_widgets = True

        self.t_title = self.add(nps.FixedText, editable=False, rely=1, relx=3, value="Select the x and y data and fit it to the function:")
        self.fun = self.add(nps.FixedText, editable=False, rely=2, relx=3, value="Function")
        self.line0 = self.add(nps.FixedText, rely=y1, relx=col1, editable=False, value="\u2501" * 250)
        # DATA
        self.xdata = self.add(twid.TArrSelect, rely=y1 + 1, relx=col1, name="x-data:")
        self.ydata = self.add(twid.TArrSelect, rely=y1 + 2, relx=col1, name="y-data:")
        self.t_desc1 = self.add(nps.FixedText, editable=False, rely=y1 + 4, relx=3, value="Select the variable which is NOT a parameter and change the settings if needed." + "\u2501" * 200)

        # PARAMETER SETTINGS
        n_vals = self.create_param_select(y1+5, col2)
        y2 = y1 + 5 + n_vals + 1
        self.line1 = self.add(nps.FixedText, rely=y2, relx=col1, editable=False, value="\u2501" * 250)
        self.b_calc = self.add(nps.ButtonPress, rely=y2 + 1, relx=1, name="Calculate", when_pressed_function=self.fit)

        # FUNCTION RESULT
        self.t_result = self.add(nps.FixedText, rely=y2 + 2, relx=3, editable=False, value="Result:")
        self.res_fun_name = self.add(nps.TitleText, rely=y2 + 3, relx=3, use_two_lines=False, name="Result name:", value="fit")
        self.res_fun = None
        self.b_store_res = self.add(nps.ButtonPress, rely=y2 + 4, relx=1, name="Store as new Function", when_pressed_function=self.save_fun)

        self.b_back = self.add(nps.ButtonPress, rely=y2 + 5, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        # PARAM RESULT
        self.t_desc2 = self.add(nps.FixedText, editable=False, rely=y2 + 6, relx=3,
                              value="Parameters Result: (press 's' on a parameter to save it)" + "\u2501" * 200)
        y3 = self.create_res_display(y2+6, col2)

        # status bar
        self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="You can use 'Tab' key for autocompletion.")
        self.status.important = True  # makes it bold and green

    def _clear_all_widgets(self, ):
        self._widgets__ = []
        self._widgets_by_id = {}
        self._next_w_id = 0
        self.nextrely = self.DEFAULT_NEXTRELY
        self.nextrelx = self.DEFAULT_X_OFFSET
        self.editw = 0  # Index of widget to edit.

    def create_param_select(self, y, col2):
        varlist = ["None"]
        if self.parentApp.function is not None:
            varlist = cl.get_needed_values(self.parentApp.function[1])
        self.varselect = self.add(nps.TitleSelectOne, rely=y, relx=3, use_two_lines=True, begin_entry_at=0, scroll_exit=True, field_width=17, max_height=len(varlist)+2,
                                  name="Variable:", value=[0], values=varlist)
        self.varoptions_desc = self.add(nps.FixedText, editable=False, rely=y, relx=col2, value="lower bound, upper bound, starting value")
        self.varoptions = {}
        for i in range(len(varlist)):
            self.varoptions.update({varlist[i]: self.add(twid.Input, rely=y+1+i, relx=col2, name=varlist[i], begin_entry_at=8, value="-inf, inf, 0", max_height=len(varlist)+1)})
        return len(varlist) + 1

    def create_res_display(self, y, col2):
        self.res_params = []
        self.res_uparams = []
        for i in range(len(self.varselect.values)):
            # create display for params
            self.res_params.append(self.add(twid.SingleArrDisplay, rely=y + 1 + i, relx=3, field_width=col2 - 5, name=self.varselect.values[i], value="---"))
            # same for u params
            self.res_uparams.append(self.add(twid.SingleArrDisplay, rely=y + 1 + i, relx=col2, name="u" + self.varselect.values[i], value="---"))
        return len(self.res_params)

    def pre_edit_loop(self):
        """
        updates the vectornames and vectors widgets
        detects, which values are needed to calculate the function
        """
        # Remove all widgets and recreate them without variable widgets
        self._clear_all_widgets()
        self.create()

        self.fun.value = f"{self.parentApp.function[0]}={self.parentApp.function[1]}"
        self.fun.update()
        # set cursor to first var
        self.editw = 0

    def fit(self):
        xdata = self.xdata.get_arr()
        ydata = self.xdata.get_arr()
        if xdata is None:
            self.status.value = "Invalid x-data"
        elif ydata is None:
            self.status.value = "Invalid y-data"
        else:
            # put the NOT parameter at the beginning of the variable list, params have to be after variable for scipy optimize
            variables = self.varselect.values.copy()
            variables.insert(0, variables.pop(self.varselect.value[0]))
            # create a dictionary for the parameter settings
            settings = {}
            for key, wid in self.varoptions.items():
                settings.update({key: wid.value})

            p0, pmin, pmax = calc.get_p0_bounds(variables[1:], settings)
            self.res_fun, params, uparams = calc.str_fit(self.parentApp.function[1], xdata, ydata, variable=variables[0], p0=p0, bounds=(pmin, pmax))
            self.t_result.value = "Result: " + str(self.res_fun)
            self.t_result.update()
            for i in range(len(params)):
                # store the parameter values in the SingleArrDisplay.array
                self.res_params[i].array = params[i]
                self.res_uparams[i].array = uparams[i]
                # display the values
                self.res_params[i].value = str(params[i])
                self.res_uparams[i].value = str(uparams[i])
                # update widgets
                self.res_params[i].update()
                self.res_uparams[i].update()

    def save_fun(self):
        if self.res_fun is not None and self.res_fun_name.value != "":
            self.parentApp.ses.add_funs([f"{self.res_fun_name.value}={self.res_fun}"])
        else:
            nps.notify_confirm("Could not save function: Either 'name' or function is None.")

