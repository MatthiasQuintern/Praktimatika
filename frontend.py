import os
import sys
import npyscreen as nps
import sessions
import curses
import re
import sheet_read as sr
import sympy as sy
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
        result = sessions.check_read_file(self.path.value)
        # if path is not a readable file
        if not result[0]:
            self.status.value = result[1]
        # if path is a readable file
        else:
            # update the sessions vectors
            self.parentApp.ses.vecs.update(sr.get_vectors(sr.read_table(self.path.value)))
            self.status.value = f"Smart-Imported Vectors from {self.path.value}"


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
        self.status.value = sessions.check_save_session(self.parentApp.ses, self.path.value, self.filename.value)
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
        self.parentApp.ses.add_funs(self.to_add.values, replace=self.c_replace.value)
        self.status.update()

    def pre_edit_loop(self):
        # clear the add-box
        self.to_add.values = []
        self.status.value = "Press 'Enter' to start/stop writing in the textbox."


class AddFunBox(nps.MultiLineEditableBoxed):
    def when_cursor_moved(self):
        self.parent.status.value += "Seems valid?"
        for line in self.values:
            if not sessions.check_valid_fun(line):
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
# FUNCTION MENU
#
class FuncMenu(nps.FormBaseNew):
    DEFAULT_LINES = 12
    DEFAULT_COLUMNS = 90
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.FixedText, rely=1, relx=3, value="Select the action to perform on the function:")
        self.fun = self.add(nps.FixedText, rely=2, relx=3, value="None")
        self.options = self.add(FuncAction, rely=5, relx=3)
        # self.b_derivate = self.add(nps.ButtonPress, rely=5, relx=1, name="Derivate Function", when_pressed_function=self.dummy)
        # self.b_back = self.add(nps.ButtonPress, rely=6, relx=1, name="Go Back", when_pressed_function=self.parentApp.switchFormPrevious)
        self.status = self.add(nps.FixedText, rely=9, relx=3, value="You can use 'Tab' key for autocompletion.")
        self.status.important = True  # makes it bold and green

    def dummy(self):
        nps.notify_confirm(f"{self.fun.value}: ")


class FuncAction(nps.MultiLineAction):
    """Widget containing actions to perform on functions"""
    def __init__(self, *args, **keywords):
        super(FuncAction, self).__init__(*args, **keywords)
        self.pa = self.parent.parentApp
        self.function = sy.sympify("test(x)")
        self.actions = {
            "Output Latex":         self.pa.output(sy.latex(self.function)),
            "Output Function":      self.pa.output(str(self.function))
        }
        self.values = self.actions.keys()

    def actionHighlighted(self, act_on_this, key_press):
        nps.notify_confirm(f"{act_on_this, key_press}")

    def set_up_handlers(self):
        # copied from wgmultiline.py
        super().set_up_handlers()
        # define all keys on which the widget reacts
        self.handlers.update({
                        ord('l'):           self.h_act_on_highlighted,
                    })


#
# HOME MENU
#

class MultiLineAction(nps.MultiLineAction):
    """Main Widget in the home screen, to display functions, vectors, variables etc..."""
    def actionHighlighted(self, act_on_this, key_press):
        nps.notify_confirm(f"{act_on_this, key_press}")

    def set_up_handlers(self):
        # copied from wgmultiline.py
        super(MultiLineAction, self).set_up_handlers()
        # define all keys on which the widget reacts
        self.handlers.update({
                        curses.ascii.TAB:    self.h_exit_down,
                        # curses.KEY_DOWN:     self.h_exit_down,
                        # curses.KEY_UP:       self.h_exit_up,
                        curses.KEY_LEFT:     self.h_exit_left,
                        curses.KEY_RIGHT:    self.h_exit_right,
                        "^P":                self.h_exit_up,
                        "^N":                self.h_exit_down,
                        curses.ascii.ESC:    self.h_exit_escape,
                        curses.KEY_MOUSE:    self.h_exit_mouse,
                        curses.ascii.NL:    self.parent.parentApp.open_m_fun,
                        curses.ascii.CR:    self.parent.parentApp.open_m_fun,
                        ord('d'):           self.h_act_on_highlighted,
                        ord('x'):           self.h_act_on_highlighted,
                        curses.ascii.SP:    self.h_act_on_highlighted,

                    })


class BoxMultiLineAction(nps.BoxTitle):
    _contained_widget = MultiLineAction


class MainSelect(nps.TitleSelectOne):
    def when_value_edited(self):
        self.parent.change_main()

    def set_up_handlers(self):
        # copied from wgmultiline.py
        super(MainSelect, self).set_up_handlers()
        # define all keys on which the widget reacts
        self.handlers.update({
                        curses.KEY_LEFT:     self.h_exit_left,
                        curses.KEY_RIGHT:    self.h_exit_right,
                    })


class HomeMenu(nps.FormBaseNewWithMenus):
    MENU_KEY = "^S"
    def afterEditing(self):
        pass
        # self.parentApp.setNextForm('menus')

    def create(self):
        MAXY, MAXX = self.lines, self.columns
        self.b_import = self.add(nps.ButtonPress, rely=8, relx=0, name="Import spreadsheet", when_pressed_function=self.call_import)
        self.b_save = self.add(nps.ButtonPress, rely=9, relx=0, name="Save Session", when_pressed_function=self.call_save)
        self.b_add_fun = self.add(nps.ButtonPress, rely=10, relx=0, name="Add Function", when_pressed_function=self.call_add_fun)
        self.pager = self.add(BoxMultiLineAction, editable=True, exit_left=True, scroll_exit=True, relx=35, rely=11, max_height=10, name="Hier steht zeug:",
                              values=["alle", "meine", "entchen"])

        self.main_select = self.add(MainSelect, begin_entry_at=0, scroll_exit=True, rely=25, max_height=5, name="Select what do display:", value=[0], values=["Functions", "Variables", "Vectors", "Constants"])
        self.status = self.add(nps.Textfield, rely=MAXY - 2 - self.BLANK_LINES_BASE, relx=1, editable=False)
        self.status.important = True  # makes it bold and green

        self.command = self.add(nps.TextCommandBox, name="command box", rely=MAXY - 1 - self.BLANK_LINES_BASE, relx=0, )
        self.action_controller = nps.ActionControllerSimple()


        # Todo: unnecessary lines?

        self.nextrely = 2

        self.status.value = 'Command Line:'

        # OWN STUFF
        self.mmenu = self.new_menu(name="Select Theme:", shortcut="^M")  # Todo: shortcut not working
        self.mmenu.addItemsFromList([("Light Font", change_setting, None, None, ("theme", nps.Themes.TransparentThemeLightText)),
                                     ("Dark Font", change_setting, None, None, ("theme", nps.Themes.TransparentThemeDarkText)),
                                     ("Default", change_setting, None, None, ("theme", nps.Themes.DefaultTheme)),
                                     ("Colourful", change_setting, None, None, ("theme", nps.Themes.ColorfulTheme)),
                                     ("Elegant", change_setting, None, None, ("theme", nps.Themes.ElegantTheme))])

        self.m_quit = self.new_menu(name="Save and Quit Menu", shortcut="^S")  # Todo: shortcut not working
        self.m_quit.addItemsFromList([("Save", save_session, None, None, (self.parentApp.ses,)),
                                     ("Save As", self.parentApp.switchForm, None, None, ("save",)),
                                     ("Quit without Saving", exit_app, None, None, None)])

        self.m_save = self.new_menu(name="Quicksave PKTSession")
        self.m_save.addItem("Quicksave", save_session, None, None, (self.parentApp.ses,))

    def pre_edit_loop(self):
        # main box
        self.change_main()

    def change_main(self):
        if self.main_select.value:
            name = self.main_select.values[self.main_select.value[0]]
            self.pager.values = self.parentApp.ses.get_dict(name)
            self.pager.name = name

        self.pager.update()

    def call_import(self):
        self.parentApp.switchForm("import")

    def call_save(self):
        self.parentApp.switchForm("save")

    def call_add_fun(self):
        self.parentApp.switchForm("add_fun")


#
# STARTUP
#


class StartupMenu(nps.FormBaseNewWithMenus):
    def create(self):
        MAXY, MAXX = self.lines, self.columns
        self.title = self.add(nps.FixedText, name="Title", editable=False, value=f"Welcome to Praktimatika:{MAXY, MAXX, self.BLANK_LINES_BASE}")
        self.select = self.add(nps.TitleSelectOne, scroll_exit=True, max_height=2, name='Load Session?', value=[0], values=['No, create new session', 'Load PKTSession from file (.ptk)'])
        self.input_file = self.add(nps.TitleFilenameCombo, name="Select File")
        self.status = self.add(nps.Textfield, rely=MAXY - 3, relx=2, editable=False, value="Status: Waiting for user selection.")
        self.b_start = self.add(nps.MiniButtonPress, rely=8, name="Start", when_pressed_function=self.on_ok)
        self.b_exit = self.add(nps.MiniButtonPress, rely=8, relx=10, name="Exit", when_pressed_function=exit_app)
        # self.button = self.add(nps.MiniButtonPress, name="Start", when_pressed_function=self.start_conversion)
        # OWN STUFF
        self.mmenu = self.new_menu(name="Select Theme:", shortcut="^G")  # Todo: shortcut not working
        self.mmenu.addItemsFromList([("Light Font", nps.setTheme, None, None, (nps.Themes.TransparentThemeLightText, )),
                                     ("Dark Font", nps.setTheme, None, None, (nps.Themes.TransparentThemeDarkText,)),
                                     ("Default", nps.setTheme, None, None, (nps.Themes.DefaultTheme,)),
                                     ("Colourful", nps.setTheme, None, None, (nps.Themes.ColorfulTheme,)),
                                     ("Elegant", nps.setTheme, None, None, (nps.Themes.ElegantTheme,))])

    def on_ok(self):
        # TODO: Exception Handling
        # create new session
        if self.select.value == [0]:
            self.parentApp.ses = sessions.PKTSession(os.getcwd() + "/new_session.ptk")
            self.parentApp.switchForm('home')
            self.status.value = "Status: Creating new session."
        # load session
        elif self.select.value == [1]:
            self.parentApp.ses = sessions.load_session(self.input_file.value)
            self.parentApp.switchForm('home')
            self.status.value = f"Status: Loading session from: {self.input_file.value}"
            nps.notify_confirm(f"Status: Loading session from: {self.input_file.value}")
        else:
            self.status.value = "Status: Please select wether you want to load a session or create a new one and then press 'Start'."


#
# METHODS
#


def save_session(session: sessions.PKTSession):
    return sessions.check_save_session(session)


def exit_app():
    if nps.notify_yes_no("Are you sure you want to exit Praktimatika?", title='Exit Praktimatika'):
        sys.exit()


def change_setting(setting, value):
    # TODO
    pass


#
# APPLICATION
#


class Praktimatika(nps.NPSAppManaged):
    """Managed Application. Contains the Praktimatika PKTSession, so that all forms and widgets can access it."""
    def onStart(self):
        self.print_out = False
        # temp:
        # self.ses = sessions.load_session("session.ptk")
        self.ses = None
        # nps.setTheme(nps.Themes.TransparentThemeLightText)
        start = self.addForm("MAIN", StartupMenu, name='Praktimatika Startup')
        # self.addForm("start", StartupMenu, name='Praktimatika Startup')
        home = self.addForm("home", HomeMenu, name="Praktimatika Home")
        # Small Menues:
        save = self.addForm("save", SaveMenu, name="Save Praktimatika PKTSession")
        impor = self.addForm("import", ImportMenu, name="Import vectors from a spreadsheet")
        func = self.addForm("m_fun", FuncMenu, name="Function Menu")
        # Add Menus
        add_fun = self.addForm("add_fun", AddFun, name="Add a function")

    def open_m_fun(self, *args):
        nps.notify_confirm(str(args))
        self.switchForm("m_fun")

    def output(self, string: str):
        if self.print_out:
            pass
        # todo
        nps.notify_confirm(string)
if __name__ == '__main__':
    TestApp = Praktimatika().run()













