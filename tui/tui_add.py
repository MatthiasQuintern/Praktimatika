import curses
import npyscreen as nps
import sympy as sy
from tools import checks
from tui import tui_widgets as twid

class AddVec(nps.FormBaseNew):
    DEFAULT_LINES = 20
    DEFAULT_COLUMNS = 110
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.MultiLine, rely=1, relx=3, editable=False, values=["Enter your vector line by line, values separated with ',' eg:", "\tv = [2, 0.5, .3, 4.]", "\tw=[42]"])
        # todo: change addfunbox
        self.to_add = self.add(AddFunBox, rely=4, relx=3, max_height=7, exit_right=True, scroll_exit=True)
        self.c_replace = self.add(twid.CheckBox, rely=12, relx=3, editable=True, name="Replace conflicting vectors", value=False)
        self.b_add = self.add(nps.ButtonPress, rely=14, relx=1, name="Add Vectors", when_pressed_function=self.add_vecs)
        self.b_back = self.add(nps.ButtonPress, rely=15, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        self.status = self.add(nps.FixedText, rely=16, relx=3, editable=False, value="Press 'Enter' to start/stop writing in the textbox.")
        self.status.important = True  # makes it bold and green

    def add_vecs(self):
        self.status.value = self.parentApp.ses.add_vecs(self.to_add.values, replace=self.c_replace.value)
        self.status.update()

    def pre_edit_loop(self):
        # clear the add-box
        self.to_add.values = []
        self.status.value = "Press 'Enter' to start/stop writing in the textbox."


#
# ADD FUNCTION/VECTOR MENU
#
class AddFun(nps.FormBaseNew):
    DEFAULT_LINES = 20
    DEFAULT_COLUMNS = 110
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.MultiLine, rely=1, relx=3, editable=False, values=["Enter your functions line by line, eg:", "\tf = cos(2*x+4) / exp(y)", "\tg = x**2 + z**(x + 2)"])
        self.to_add = self.add(AddFunBox, rely=4, relx=3, max_height=7, exit_right=True, scroll_exit=True)
        self.c_replace = self.add(nps.Checkbox, rely=12, relx=3, editable=True, name="Replace conflicting functions", value=False)
        self.c_autoadd_vars = self.add(nps.Checkbox, rely=13, relx=3, editable=True, name="Automatically add missing variables", value=False)
        self.b_add = self.add(nps.ButtonPress, rely=14, relx=1, name="Add Functions", when_pressed_function=self.add_funs)
        self.b_back = self.add(nps.ButtonPress, rely=15, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        self.status = self.add(nps.FixedText, rely=16, relx=3, editable=False, value="Press 'Enter' to start/stop writing in the textbox.")
        self.status.important = True  # makes it bold and green

    def add_funs(self):
        try:
            self.status.value = self.parentApp.ses.add_funs(self.to_add.values, replace=self.c_replace.value)
            self.status.update()
        except sy.SympifyError as ex:
            nps.notify_confirm(str(ex))

    def pre_edit_loop(self):
        # clear the add-box
        self.to_add.values = []
        self.status.value = "Press 'Enter' to start/stop writing in the textbox."


class AddFunBox(nps.MultiLineEditableBoxed):
    def when_cursor_moved(self):
        self.parent.status.value += "Seems valid?"
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
