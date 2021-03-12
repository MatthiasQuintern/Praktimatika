import re
import npyscreen as nps
from tools import latex
from tui import tui_widgets as twid


class LatexTable(twid.BaseForm):
    DEFAULT_LINES = 15
    DEFAULT_COLUMNS = 120
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.desc = self.add(nps.MultiLine, rely=1, relx=3, editable=False, values=["Generate a Latex Table like this:", "v1 & v2 pm uv2 & v3", "The Vectors must already exist and all have the same length."])
        # input vectors
        self.format = self.add(nps.TitleText, rely=5, relx=3, use_two_lines=False, name="Format")
        self.box = self.add(nps.CheckBox, rely=6, relx=3, name="Grid/Box-Lines")
        self.b_table = self.add(nps.ButtonPress, rely=7, relx=1, name="Create Latex Table", when_pressed_function=self.table)
        self.b_back = self.add(nps.ButtonPress, rely=8, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)

        # status
        self.status = self.add(nps.FixedText, rely=self.max_y - 4, relx=3, editable=False, value="")
        self.status.important = True  # makes it bold and green

    def table(self):
        ready = True
        vectors = {}
        vecnames = re.split("&|pm", self.format.value.replace(" ", ""))
        for vecname in vecnames:
            if vecname in self.parentApp.ses.vecs:
                vectors.update({vecname: self.parentApp.ses.vecs[vecname]})
            else:
                ready = False
                self.status.value = f"Invalid Vector Name: {vecname}"
                break
        if ready:
            table = latex.latex_table(self.format.value, vectors, box=self.box.value)
            self.parentApp.output(table)
        self.status.update()