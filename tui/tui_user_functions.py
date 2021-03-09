import npyscreen as nps
import curses
import numpy as np
import calc as cl
import sympy as sy
from tools import checks
from tui import tui_widgets as twid
from maths import error


#
# FUNCTION MENU
#
class UserFuncMenu(nps.FormBaseNew):
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

    def dummy(self):
        nps.notify_confirm(f"{self.fun.value}: ")


class UserFuncCalc2(nps.FormBaseNew):
    """
    lets the user input the values/vectors to calculate a function
    the function is used is the parentApp.function, which is selected
    """
    DEFAULT_LINES = 25
    DEFAULT_COLUMNS = 120
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.cycle_widgets = True

        self.title = self.add(nps.FixedText, editable=False, rely=1, relx=3, value="Select the values to calculate the function")
        self.fun = self.add(nps.FixedText, editable=False, rely=2, relx=3, value="Function")
        self.vars = {}
        self.b_calc = self.add(nps.ButtonPress, rely=14, relx=1, name="Calculate", when_pressed_function=self.calc)
        self.result = self.add(nps.FixedText, rely=15, relx=3, value="Result:")
        self.result_val = None     # store the value of the result, so that it can be processed
        self.res_name = self.add(nps.TitleText, rely=16, relx=3, use_two_lines=False, name="Result name:", value="res")
        self.b_store_res = self.add(nps.ButtonPress, rely=18, relx=1, name="Store Result as Vector", when_pressed_function=self.save_res)
        self.b_back = self.add(nps.ButtonPress, rely=19, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        # status bar
        # self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="You can use 'Tab' key for autocompletion.")
        # self.status.important = True  # makes it bold and green

    def _clear_all_widgets(self, ):
        self._widgets__ = []
        self._widgets_by_id = {}
        self._next_w_id = 0
        self.nextrely = self.DEFAULT_NEXTRELY
        self.nextrelx = self.DEFAULT_X_OFFSET
        self.editw = 0  # Index of widget to edit.

    def _count_editable(self):
        n = 0
        for w in self._widgets__:
            if w.editable and not w.hidden:
                n += 1
        return n

    def pre_edit_loop(self):
        """
        updates the vectornames and vectors widgets
        detects, which values are needed to calculate the function
        """
        # Remove all widgets and recreate them without variable widgets
        self._clear_all_widgets()
        self.create()

        varlist = cl.get_needed_values(self.parentApp.function[1])

        for i in range(len(varlist)):
            value = ""
            # check if the varname is a constant or already defined vector
            if varlist[i] in self.parentApp.ses.consts.keys():
                value = self.parentApp.ses.consts[varlist[i]]
            elif varlist[i] in self.parentApp.ses.vecs.keys():
                value = self.parentApp.ses.vecs[varlist[i]]
            # value must be string, otherwise there can be unfixable TypeError with 1-element numpy arrays
            self.vars.update({varlist[i]: self.add(twid.TVecSelect, rely=3 + i, relx=3, name=f"{varlist[i]}:", value=str(value))})

        self.fun.value = f"{self.parentApp.function[0]}={self.parentApp.function[1]}"
        self.fun.update()
        # set cursor to first var
        self.editw = self._count_editable() - 1

    def calc(self):
        d = {}  # dict with varname: vector pairs
        for name, wid in self.vars.items():
            # IF THE CHECKS DON'T PASS, THE INPUT VALUE IS STILL INVALID/NONE!
            value = wid.value
            if str(value) in self.parentApp.ses.vecs:
                value = self.parentApp.ses.vecs[str(value)]
            # check if value is an array with numbers
            elif checks.is_number(value):
                value = float(value)
            # check if value is a number
            # elif checks.is_number_array(value):
            #     value = np.array(value, dtype=float)
            else:
                value = checks.str_to_arr(str(value))[1]
                # nps.notify_confirm(f"Can not convert {value} to a number or array")
            d.update({name: value})
        try:
            self.result_val = cl.calculate(self.parentApp.function[1], d)
            self.result.value = f"Result: {self.result_val}"
        except TypeError as ex:
            self.parentApp.output(ex)
        self.result.update()

    def save_res(self):
        if (checks.is_number(self.result_val) or checks.is_number_array(self.result_val)) and self.res_name.value != "":
            self.parentApp.ses.add_vec(self.res_name.value, np.array(self.result_val))
        else:
            nps.notify_confirm("Could not save vector!")


class ErrorPropagation(nps.FormBaseNew):
    """
    Returns
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