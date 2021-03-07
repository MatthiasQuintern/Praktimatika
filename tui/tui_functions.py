import npyscreen as nps
import numpy as np
from tools import checks
from maths import median

from tui import tui_widgets as twid

#
# FORMS
#
class SaveVec(nps.FormBaseNew):
    """
    Menu to save vectors. BEFORE it is called, the "vector" attribute must be set to the vector
    """
    DEFAULT_LINES = 20
    DEFAULT_COLUMNS = 120
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.FixedText, rely=1, relx=3, editable=False, value="Save Vector")
        self.vector = None
        self.vector_display = self.add(nps.FixedText, rely=5, relx=3, editable=False, name="Select a name for:", value="None")
        self.vecname = self.add(nps.Textfield, rely=5, relx=3, name="Name:")
        self.b_save = self.add(nps.ButtonPress, rely=5, relx=1, name="Calculate Weighted Median", when_pressed_function=self.save_vec)
        self.b_back = self.add(nps.ButtonPress, rely=6, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)

        # status
        self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="You can use 'Tab' key for autocomplete Vector names.")
        self.status.important = True  # makes it bold and green

    def pre_edit_loop(self):
        self.vector_display.value = str(self.vector)
        self.status.value = "You can use 'Tab' key for autocomplete Vector names."

    def save_vec(self):
        ready = True
        if not checks.is_number_array(self.vector):
            ready = False
            self.status.value = "Invalid Vector"
        if self.vecname.value == "":
            ready = False
            self.status.value = "Please Enter a Valid Vectorname"
        # save and quit
        if ready:
            self.status.value = self.parentApp.ses.add_vec(self.vecname.value, np.array(self.vector, dtype=float))
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
        self.result_name = self.add(nps.TitleMultiLine, rely=6, relx=3, editable=False, use_two_lines=True, begin_entry_at=0, name="Result:", values=["Weighted Median", "Internal Uncertainty", "External Uncertainty"])
        #todo: make newvecddisply work
        self.result = self.add(twid.NewVecDisplay, rely=6, relx=25, max_height=5, editable=True, values=["None", "None", "None"])
        # status
        self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="You can use 'Tab' key for autocomplete Vector names.")
        self.status.important = True  # makes it bold and green

    def calc(self):
        ready = True
        if not self.vector.value in self.parentApp.ses.vecs:
            ready = False
            self.status.value = "Invalid value vector."
        if not self.unc_vector.value in self.parentApp.ses.vecs:
            ready = False
            self.status.value = "Invalid uncertainty vector."
        if ready:
            if not len(self.parentApp.ses.vecs[self.vector.value]) == len(self.parentApp.ses.vecs[self.unc_vector.value]):
                ready = False
                self.status.value = "Vectors do not have the same length."
            else:
                result = median.weighted_median(self.parentApp.ses.vecs[self.vector.value], self.parentApp.ses.vecs[self.unc_vector.value])
                self.result.values = [str(val) for val in result]
                nps.notify_confirm(self.result.values)
                self.result.update()
        self.status.update()



