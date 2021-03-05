import npyscreen as nps
import curses
import numpy as np
import calc as cl
import sympy as sy
import checks


#
# FUNCTION MENU
#
class UserFuncMenu(nps.FormBaseNew):
    DEFAULT_LINES = 12
    DEFAULT_COLUMNS = 90
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.FixedText, rely=1, relx=3, value="Select the action to perform on the function:")
        self.fun = self.add(nps.FixedText, rely=2, relx=3, value="None")
        self.options = self.add(UserFuncAction, rely=5, relx=3)
        # self.b_derivate = self.add(nps.ButtonPress, rely=5, relx=1, name="Derivate Function", when_pressed_function=self.dummy)
        # self.b_back = self.add(nps.ButtonPress, rely=6, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        self.status = self.add(nps.FixedText, rely=9, relx=3, value="You can use 'Tab' key for autocompletion.")
        self.status.important = True  # makes it bold and green

    def dummy(self):
        nps.notify_confirm(f"{self.fun.value}: ")


class UserFuncAction(nps.MultiLineAction):
    """Widget containing actions to perform on functions"""
    def __init__(self, *args, **keywords):
        super(UserFuncAction, self).__init__(*args, **keywords)
        self.pa = self.parent.parentApp
        self.actions = {
            "Calculate":            (self.pa.switchForm, "m_fun_calc"),
            "Output Latex":         (self.pa.output, sy.latex(self.pa.function[1])),
            "Output Function":      (self.pa.output, str(self.pa.function[1])),
            "Delete":               (self.delete_fun, None),
            "Go Back":              (self.pa.switchForm, "home")
        }
        self.values = list(self.actions.keys())

    def actionHighlighted(self, act_on_this, key_press):
        nps.notify_confirm(f"{act_on_this, key_press}")
        # function(arg) as defined in self.actions
        self.actions[act_on_this][0](self.actions[act_on_this][1])

    def set_up_handlers(self):
        # copied from wgmultiline.py
        super().set_up_handlers()
        # define all keys on which the widget reacts
        self.handlers.update({
                        ord('l'):           self.h_act_on_highlighted,
                        ord('x'):           self.h_act_on_highlighted,
                        curses.ascii.NL:    self.h_act_on_highlighted,
                    })

    def delete_fun(self, none):
        if nps.notify_yes_no("Do you really want to delete the function?"):
            self.pa.ses.funs.pop(self.pa.function[0])

class UserFuncCalc(nps.FormBaseNew):
    """
    lets the user input the values/vectors to calculate a function
    the function is used is the parentApp.function, which is selected
    """
    DEFAULT_LINES = 25
    DEFAULT_COLUMNS = 120
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.FixedText, editable=False, rely=1, relx=3, value="Select the values to calculate the function")
        self.fun = self.add(nps.FixedText, editable=False, rely=2, relx=3, value="Function")
        self.varnames = self.add(nps.MultiLine, editable=False, rely=6, relx=3, max_height=8, begin_entry_at=0, name="Var:")
        self.vars = self.add(BTMultiLineEdit, exit_left=True, exit_right=True, scroll_exit=True, rely=5, relx=20, max_height=8, begin_entry_at=0, name="Value:")
        self.b_calc = self.add(nps.ButtonPress, rely=14, relx=1, name="Calculate", when_pressed_function=self.calc)
        self.result = self.add(nps.FixedText, rely=15, relx=3, value="Result:")
        self.result_val = None     # store the value of the result, so that it can be processed
        self.res_name = self.add(nps.TitleText, rely=16, relx=3, use_two_lines=False, name="Result name:", value="res")
        self.b_store_res = self.add(nps.ButtonPress, rely=18, relx=1, name="Store Result as Vector", when_pressed_function=self.save_res)
        self.b_back = self.add(nps.ButtonPress, rely=19, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        # status bar
        # self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="You can use 'Tab' key for autocompletion.")
        # self.status.important = True  # makes it bold and green

    def pre_edit_loop(self):
        """
        updates the vectornames and vectors widgets
        detects, which values are needed to calculate the function
        """
        varlist = cl.get_needed_values(self.parentApp.function[1])
        self.vars.values, self.varnames.values = ["" for i in range(len(varlist))], ["" for i in range(len(varlist))]  # make the list the right length
        for i in range(len(varlist)):
            self.varnames.values[i] = varlist[i]
            # check if the varname is a constant or already defined vector
            if varlist[i] in self.parentApp.ses.consts.keys():
                self.vars.values[i] = self.parentApp.ses.consts[varlist[i]]
            elif varlist[i] in self.parentApp.ses.vecs.keys():
                self.vars.values[i] = self.parentApp.ses.vecs[varlist[i]]

        self.fun.value = f"{self.parentApp.function[0]}={self.parentApp.function[1]}"
        self.fun.update()
        self.vars.update()
        self.varnames.update()

    def calc(self):
        d = {}  # dict with varname: vector pairs
        for i in range(len(self.varnames.values)):
            # IF THE CHECKS DON'T PASS, THE INPUT VALUE IS STILL INVALID!
            value = self.vars.values[i]
            if str(value) in self.parentApp.ses.vecs:
                value = self.parentApp.ses.vecs[str(value)]
            # check if value is an array with numbers
            if checks.is_number(value):
                value = float(value)
            # check if value is a number
            elif checks.is_number_array(value):
                value = np.array(value, dtype=float)
            d.update({self.varnames.values[i]: value})
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

#
# Box-Title widgets
#
class BTMultiLineEdit(nps.BoxTitle):
    _contained_widget = nps.MultiLineEditable


class BTMultiLine(nps.BoxTitle):
    _contained_widget = nps.MultiLine