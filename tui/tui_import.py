import npyscreen as nps
from tools import sheet_read as sr, checks
import os

#
# SPREADSHEET IMPORT MENU
#
class ImportMenu(nps.FormBaseNew):
    DEFAULT_LINES = 12
    DEFAULT_COLUMNS = 90
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):

        path = os.path.expanduser("~")

        self.title = self.add(nps.FixedText, rely=1, relx=3, value="Select the the spreadsheet to import data from:")
        self.path = self.add(nps.TitleFilenameCombo, rely=2, relx=3, name="Path:", value=path)
        self.sep = self.add(nps.TitleFilenameCombo, rely=3, relx=3, name=".csv seperator:", value=",")
        self.b_man_im = self.add(nps.ButtonPress, rely=5, relx=1, name="Manual Import", when_pressed_function=self.man_import)
        self.b_smt_im = self.add(nps.ButtonPress, rely=6, relx=1, name="Smart Import", when_pressed_function=self.smart_import)
        # self.b_save_as = self.add(nps.ButtonPress, rely=4, relx=1, name="Save as", when_pressed_function=exit_app)
        self.b_back = self.add(nps.ButtonPress, rely=7, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        self.status = self.add(nps.FixedText, rely=9, relx=3, value="'Smart Import' looks for strings with values in one column and imports them as vectors")
        self.status.important = True  # makes it bold and green

    def man_import(self):
        self.status = "Manual import is not implemented yet"

    def smart_import(self):
        result = checks.is_readable_file(self.path.value)
        # if path is not a readable file
        if not result[0]:
            self.status.value = result[1]
        # if path is a readable file
        else:
            # update the sessions vectors
            self.parentApp.ses.vecs.update(sr.get_vectors(sr.read_table(self.path.value)))
            self.status.value = f"Smart-Imported Vectors from {self.path.value}"

