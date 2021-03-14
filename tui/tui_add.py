import curses
import npyscreen as nps
import sympy as sy
from tools import checks
from tui import tui_widgets as twid


class AddArr(twid.BaseForm):
    DEFAULT_LINES = 30
    DEFAULT_COLUMNS = 110
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        y0 = 7
        y1 = y0 + 7
        self.desc = self.add(nps.MultiLine, rely=1, relx=3, editable=False, values=["Enter your array or number line by line, array values separated with ','",
                                                                                    "Array can reference other array, Numpy Array slicing is supported",
                                                                                    "Operations are performed from back to front, '()' are not allowed (yet?)",
                                                                                    "    v = [2, 0.5, .3, 4., 7, 5, -5.3]",
                                                                                    "    w = 2 * v[2::3] / 5"])
        self.to_add = self.add(AddFunBox, rely=y0, relx=3, max_height=7, exit_right=True, scroll_exit=True)
        self.c_replace = self.add(twid.CheckBox, rely=y1+1, relx=3, editable=True, name="Replace conflicting arrays", value=False)
        self.b_add = self.add(nps.ButtonPress, rely=y1+2, relx=1, name="Add Arrays", when_pressed_function=self.add_arrs)
        self.b_back = self.add(nps.ButtonPress, rely=y1+3, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="Press 'Enter' to start/stop writing in the textbox.")
        self.status.important = True  # makes it bold and green

    def add_arrs(self):
        self.status.value = self.parentApp.ses.add_arrs(self.to_add.values, replace=self.c_replace.value)
        self.status.update()

    def pre_edit_loop(self):
        # clear the add-box
        self.to_add.values = []
        self.status.value = "Press 'Enter' to start/stop writing in the textbox."


#
# ADD FUNCTION
#
class AddFun(twid.BaseForm):
    DEFAULT_LINES = 20
    DEFAULT_COLUMNS = 110
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.MultiLine, rely=1, relx=3, editable=False, values=["Enter your functions line by line, eg:", "\tf = cos(2*x+4) / exp(y)", "\tg = x**2 + z**(x + 2)"])
        self.to_add = self.add(AddFunBox, rely=4, relx=3, max_height=7, exit_right=True, scroll_exit=True)
        self.c_replace = self.add(twid.CheckBox, rely=12, relx=3, editable=True, name="Replace conflicting functions", value=True)
        self.c_autoadd_vars = self.add(twid.CheckBox, rely=13, relx=3, editable=True, name="Automatically add missing variables", value=True)
        self.b_add = self.add(nps.ButtonPress, rely=14, relx=1, name="Add Functions", when_pressed_function=self.add_funs)
        self.b_back = self.add(nps.ButtonPress, rely=15, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        self.status = self.add(nps.FixedText, rely=16, relx=3, editable=False, value="Press 'Enter' to start/stop writing in the textbox.")
        self.status.important = True  # makes it bold and green

    def add_funs(self):
        try:
            self.status.value = self.parentApp.ses.add_funs(self.to_add.values, replace=self.c_replace.value, auto_vars=self.c_autoadd_vars.value)
            self.status.update()
        except sy.SympifyError as ex:
            nps.notify_confirm(str(ex))

    def pre_edit_loop(self):
        # clear the add-box
        self.to_add.values = []
        self.status.value = "Press 'Enter' to start/stop writing in the textbox."


class AddFunBox(nps.MultiLineEditableBoxed):
    def when_cursor_moved(self):
        self.parent.status.value += ""
        for line in self.values:
            if not checks.is_valid_fun(line):
                self.parent.status.value = f"Invalid function: {line}"
        self.parent.status.update()

    def set_up_handlers(self):
        # copied from wgmultiline.py
        super().set_up_handlers()
        # define all keys on which the widget reacts
        self.handlers.update({
                        curses.ascii.ESC:     self.parent.parentApp.switchFormPrevious
                    })
#
# Edit Function
#
class EditFunc(twid.BaseForm):
    # DEFAULT_LINES = 13
    # DEFAULT_COLUMNS = 110
    # SHOW_ATX = 15
    # SHOW_ATY = 15

    def create(self):
        self.title = self.add(nps.FixedText, rely=1, relx=3, editable=False, value="Edit the function:")
        self.to_edit = self.add(twid.Input, rely=5, relx=3, check_method=checks.is_valid_fun, value="none")

        self.c_autoadd_vars = self.add(twid.CheckBox, rely=7, relx=3, editable=True, name="Automatically add missing variables", value=True)
        self.b_ok = self.add(nps.ButtonPress, rely=8, relx=1, name="Ok", when_pressed_function=self.change_funs)
        self.b_cancel = self.add(nps.ButtonPress, rely=8, relx=6, name="Cancel", when_pressed_function=self.parentApp.switchFormPrevious)

        self.status = self.add(nps.FixedText, rely=10, relx=3, editable=False, value="")
        self.status.important = True  # makes it bold

    def change_funs(self):
        try:
            self.status.value = self.parentApp.ses.add_funs([self.to_edit.value], auto_vars=self.c_autoadd_vars.value)
            self.status.update()
            self.parentApp.switchFormPrevious()
        except sy.SympifyError as ex:
            nps.notify_confirm(str(ex))

    def pre_edit_loop(self):
        self.to_edit.value = f"{self.parentApp.function[0]} = {self.parentApp.function[1]}"
        self.status.value = "Change the function name to save it as a new function"

