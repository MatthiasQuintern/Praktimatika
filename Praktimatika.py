import os
import sys
import npyscreen as nps
import sessions
import re
# import pandas.io.clipboard as clip  # copy to clipboard
from tui import tui_user_functions, tui_add, tui_plot
from tui import tui_functions
from tui import tui_import
from tui import tui_home
from tui import tui_tools


#
# SAVE MENU
#
class SaveMenu(nps.FormBaseNew):
    DEFAULT_LINES = 12
    DEFAULT_COLUMNS = 90
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.FixedText, rely=1, relx=3, value="Select the folder where the session should be saved:")
        self.path = self.add(nps.TitleFilename, rely=2, relx=3, name="Path:", value=os.path.expanduser("~"))
        self.filename = self.add(nps.TitleText, rely=3, relx=3, name="Filename:", value="session.ptk")
        self.b_save = self.add(nps.ButtonPress, rely=5, relx=1, name="Save PKTSession", when_pressed_function=self.save_session)
        # self.b_save_as = self.add(nps.ButtonPress, rely=4, relx=1, name="Save as", when_pressed_function=exit_app)
        self.b_back = self.add(nps.ButtonPress, rely=6, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        self.status = self.add(nps.FixedText, rely=9, relx=3, value="You can use 'Tab' key for autocompletion.")
        self.status.important = True  # makes it bold and green

    def save_session(self):
        self.status.value = self.parentApp.ses.check_save_session(path=self.path.value, filename=self.filename.value)
        self.status.update()
        self.filename.update()
        self.path.update()

    def pre_edit_loop(self):
        # update filename & filepath to be the current sessions's path
        if self.parentApp.ses:
            match = re.search(r"[a-zA-ZüÜöÖäÄ_\- ]+\.ptk$", self.parentApp.ses.path)
            if match:
                self.path.value = self.parentApp.ses.path.replace(match.group(0), "")
                self.filename.value = match.group(0)


#
# STARTUP
#
class StartupMenu(nps.FormBaseNewWithMenus):
    def create(self):
        MAXY, MAXX = self.lines, self.columns
        self.title = self.add(nps.FixedText, name="Title", editable=False, value=f"Welcome to Praktimatika Version {self.parentApp.version}")
        self.select = self.add(nps.TitleSelectOne, scroll_exit=True, max_height=2, name='Load Session?', value=[0], values=['No, create new session', 'Load PKTSession from file (.ptk)'])
        self.input_file = self.add(nps.TitleFilenameCombo, name="Select File")
        self.status = self.add(nps.Textfield, rely=MAXY - 3, relx=2, editable=False, value="Status: Waiting for user selection.")
        self.b_start = self.add(nps.ButtonPress, rely=8, name="Start", when_pressed_function=self.on_ok)
        self.b_exit = self.add(nps.ButtonPress, rely=8, relx=10, name="Exit", when_pressed_function=self.parentApp.exit_app)
        # self.button = self.add(nps.MiniButtonPress, name="Start", when_pressed_function=self.start_conversion)
        """# OWN STUFF
        self.mmenu = self.new_menu(name="Select Theme:", shortcut="^G")  # Todo: shortcut not working
        self.mmenu.addItemsFromList([("Light Font", nps.setTheme, None, None, (nps.Themes.TransparentThemeLightText, )),
                                     ("Dark Font", nps.setTheme, None, None, (nps.Themes.TransparentThemeDarkText,)),
                                     ("Default", nps.setTheme, None, None, (nps.Themes.DefaultTheme,)),
                                     ("Colourful", nps.setTheme, None, None, (nps.Themes.ColorfulTheme,)),
                                     ("Elegant", nps.setTheme, None, None, (nps.Themes.ElegantTheme,))])"""

    def on_ok(self):
        # TODO: Exception Handling
        # create new session
        if self.select.value == [0]:
            # self.parentApp.ses = sessions.PKTSession(os.getcwd() + "/new_session.ptk")
            self.parentApp.switchForm('home')
            self.status.value = "Status: Creating new session."
        # load session
        elif self.select.value == [1]:
            self.parentApp.ses = sessions.load_session(self.input_file.value)
            self.parentApp.switchForm('home')
            self.status.value = f"Status: Loading session from: {self.input_file.value}"
        else:
            self.status.value = "Status: Please select wether you want to load a session or create a new one and then press 'Start'."


#
# APPLICATION
#
class Praktimatika(nps.NPSAppManaged):
    """Managed Application. Contains the Praktimatika PKTSession, so that all forms and widgets can access it."""
    def onStart(self):
        self.version = "alpha 1"
        self.settings = {
            "print_output":    True,
            "copy_clip":    True,
            "dec_sep":      ",",
            "theme":        "Default"
        }
        self.load_settings()
        self.themes = {
            "Default": nps.Themes.DefaultTheme,
            "Colourful": nps.Themes.ColorfulTheme,
            "Elegant": nps.Themes.ElegantTheme,
            "Transparent-Light Font":  nps.Themes.TransparentThemeLightText,
            "Transparent-Dark Font":   nps.Themes.TransparentThemeDarkText,
        }

        theme = nps.Themes.DefaultTheme
        if self.settings["theme"] in self.themes:
            theme = self.themes[self.settings["theme"]]

        nps.setTheme(theme)

        # stores a selected ... to be accessible for all forms: (name, value)
        self.function = ("", None)
        self.variable = ("", None)
        self.array = ("", None)
        self.constant = ("", None)

        # temp:
        # self.ses = sessions.load_session("session.ptk")
        self.ses = sessions.PKTSession(os.getcwd() + "/new_session.ptk")
        # nps.setTheme(nps.Themes.TransparentThemeLightText)
        self.start = self.addForm("MAIN", StartupMenu, name='Praktimatika Startup')
        # self.addForm("start", StartupMenu, name='Praktimatika Startup')
        self.home = self.addForm("home", tui_home.HomeMenu, name=f"Praktimatika Home (Version {self.version})")
        # APP MENUS
        self.f_settings = self.addForm("settings", tui_home.Settings, name="Praktimatika Settings")
        self.save = self.addForm("save", SaveMenu, name="Save Praktimatika PKTSession")
        self.impor = self.addForm("import", tui_import.ImportMenu, name="Import Arrays from a spreadsheet")

        # FUNCTION MENUS
        self.func = self.addForm("m_fun", tui_user_functions.UserFuncMenu, name="Function Menu")
        self.func_calc = self.addForm("m_fun_calc", tui_user_functions.UserFuncCalc2, name="Calculation Menu")

        # BUILTIN FUNCTION MENUS
        self.weighted_median = self.addForm("weighted_median", tui_functions.WeightedMedian, name="Weighted Median")
        self.error_prop = self.addForm("error_prop", tui_user_functions.ErrorPropagation, name="Error Propagation")
        self.curve_fit = self.addForm("curve_fit", tui_user_functions.CurveFit, name="Curve Fitting")
        # PLOT MENUS
        self.plot = self.addForm("plot", tui_plot.AxesMenu, name="Plot Menu")   # remove!
        self.pl_fig = self.addForm("pl_fig", tui_plot.FigMenu, name="Plot Menu - Figure")
        self.pl_ax = self.addForm("pl_ax", tui_plot.AxesMenu, name="Plot Menu - Axis")
        self.pl_pl = self.addForm("pl_pl", tui_plot.PlotMenu, name="Plot Menu - Data")
        # Add Menus
        self.add_fun = self.addForm("add_fun", tui_add.AddFun, name="Add Functions")
        self.edit_fun = self.addForm("edit_fun", tui_add.EditFunc, name="Edit Function")
        self.add_arr = self.addForm("add_arr", tui_add.AddArr, name="Add Arrays & Values")
        self.save_arr = self.addForm("save_arr", tui_functions.SaveVec, name="Save Array")
        # TOOLS
        self.latex = self.addForm("latex_table", tui_tools.LatexTable, name="Create Latex Table")

    def output(self, message):
        message = str(message)
        if self.settings["print_output"]:
            with open("output.txt", "a") as out:
                out.write(message + "\n")
        if self.settings["copy_clip"]:
            try:
                import pandas.io.clipboard as clip  # copy to clipboard
                clip.clipboard_set(message)
            except ImportError:
                nps.notify_confirm("Con not copy output to clipboard. 'pandas' is not installed!\nPlease install python module 'pandas' to use this feature.")
        nps.notify_confirm(message)

    @staticmethod
    def show_error(message, exception: BaseException):
        """
        Shows an Error Message in an nps.notify_confirm Form
        :param message:     string, message
        :param exception:   Exception
        :return:
        """
        nps.notify_confirm(f"{message}:\n{exception}\nin file {exception.__traceback__.tb_frame.f_code.co_filename}\n"
                           f"in line {exception.__traceback__.tb_lineno}")

    @staticmethod
    def exit_app():
        if nps.notify_yes_no("Are you sure you want to exit Praktimatika?", title='Exit Praktimatika'):
            sys.exit()

    def quicksave(self):
        """
        Quicksave and set the form's status to show the output of the check_save_session method
        :return:
        """
        status = self.ses.check_save_session()

        form = self.getForm(self.ACTIVE_FORM_NAME)
        if hasattr(form, "status"):
            form.status.value = status
            form.status.update()

    def load_settings(self):
        try:
            with open("praktimatika.conf", "r") as file:
                raw_list = file.readlines()
                file.close()
                for line in raw_list:
                    if "#" in line:  # ignore commented lines
                        continue
                    line = line.replace("\n", "")
                    temp_list = line.split(" = ")
                    if temp_list[1] == "True":
                        temp_list[1] = True
                    elif temp_list[1] == "False":
                        temp_list[1] = False
                    self.settings.update({temp_list[0]: temp_list[1]})
        except FileNotFoundError:
            nps.notify_confirm("Could not load settings from 'praktimatika.conf'. File not found.")
        except IndexError:
            nps.notify_confirm("Could not load settings from 'praktimatika.conf'. Invalid file structure")

    def save_settings(self):
        with open("praktimatika.conf", "w") as file:
            text = "# Praktimatika Config File. \n" \
                   "# Content here will be overwritten when the settings are saved.\n"
            for key, val in self.settings.items():
                text += f"{key} = {val}\n"
            file.write(text)


if __name__ == '__main__':
    TestApp = Praktimatika().run()

