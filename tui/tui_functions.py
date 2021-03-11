import npyscreen as nps
import numpy as np
from tools import checks
from maths import median

from tui import tui_widgets as twid


# ẞ
# FORMS
#
class SaveVec(nps.FormBaseNew):
    """
    Menu to save vectors. BEFORE it is called, the "vector" attribute must be set to the vector
    """
    DEFAULT_LINES = 10
    DEFAULT_COLUMNS = 80
    SHOW_ATX = 14
    SHOW_ATY = 6

    def create(self):
        # self.title = self.add(nps.FixedText, rely=1, relx=3, editable=False, value="Save Vector")
        self.vector = None
        self.vector_display = self.add(nps.FixedText, rely=1, relx=3, editable=False, name="Select a name for:", value="No Vector Given")
        self.i_vecname = self.add(twid.Input, rely=2, relx=3, name="Vector Name:", value="v", check_method=checks.is_name)
        self.b_save = self.add(nps.ButtonPress, rely=3, relx=1, name="Save Vector", when_pressed_function=self.save_vec)
        self.b_back = self.add(nps.ButtonPress, rely=4, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)

        # status
        self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="You can use 'Tab' key for autocomplete Vector names.")
        self.status.important = True  # makes it bold and green

    def pre_edit_loop(self):
        self.vector_display.value = str(self.vector)
        self.status.value = ""

    def save_vec(self):
        ready = True
        if not checks.is_number_array(self.vector):
            ready = False
            self.status.value = "Invalid Vector"
        if not self.i_vecname.valid_input:
            ready = False
        # save and quit
        if ready:
            self.status.value = self.parentApp.ses.add_vec(self.i_vecname.value, np.array(self.vector, dtype=float))
            self.parentApp.switchFormPrevious()
        self.status.update()


#
# WEIGHTED MEDIAN
#
class WeightedMedian(nps.FormBaseNew):
    DEFAULT_LINES = 20
    DEFAULT_COLUMNS = 120
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        # input vectors
        self.vector = self.add(twid.TVecSelect, rely=1, relx=3, use_two_lines=False, begin_entry_at=30, name="Values (vector):")
        self.unc_vector = self.add(twid.TVecSelect, rely=2, relx=3, use_two_lines=False, begin_entry_at=30, name="Uncertainties (vector):")
        self.b_calc = self.add(nps.ButtonPress, rely=3, relx=1, name="Calculate Weighted Median", when_pressed_function=self.calc)
        self.b_back = self.add(nps.ButtonPress, rely=4, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        # result
        self.mw = self.add(twid.SingleVecDisplay, rely=6, relx=3, name="Weighted Median:", begin_entry_at=30)
        self.u_int = self.add(twid.SingleVecDisplay, rely=7, relx=3, name="Internal Uncertainty:", begin_entry_at=30)
        self.u_ext = self.add(twid.SingleVecDisplay, rely=8, relx=3, name="External Uncertainty:", begin_entry_at=30)

        # status
        self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="You can use 'Tab' key for autocomplete Vector names.")
        self.status.important = True  # makes it bold and green

    def calc(self):
        ready = True
        vec = self.vector.get_vec()
        if vec is None:
            self.status.value = "Invalid value vector."
            ready = False
        uvec = self.vector.get_vec()
        if uvec is None:
            self.status.value = "Invalid uncertainty vector."
            ready = False

        if ready:
            if not np.shape(vec) == np.shape(uvec):
                self.status.value = "Vectors do not have the same length."
            else:
                result = median.weighted_median(self.parentApp.ses.vecs[self.vector.value], self.parentApp.ses.vecs[self.unc_vector.value])
                self.mw.value, self.mw.vector = str(result[0]), result[0]
                self.u_int.value, self.u_int.vector = str(result[1]), result[1]
                self.u_ext.value, self.u_ext.vector = str(result[2]), result[2]
                self.mw.update()
                self.u_int.update()
                self.u_ext.update()
        self.status.update()



