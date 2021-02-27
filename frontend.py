import os
import sys
import npyscreen as nps
import sessions
import curses
import re
import sheet_read as sr

class MultiLineAction(nps.MultiLineAction):
    """Main Widget in the home screen, should display functions, variables etc..."""
    def actionHighlighted(self, act_on_this, key_press):
        nps.notify_confirm(f"{act_on_this, key_press}")

    def set_up_handlers(self):
        # copied from wgmultiline.py
        super(MultiLineAction, self).set_up_handlers()
        # define all keys on which the widget reacts
        self.handlers.update({
                    curses.ascii.NL:    self.h_act_on_highlighted,
                    curses.ascii.CR:    self.h_act_on_highlighted,
                    ord('d'):           self.h_act_on_highlighted,
                    ord('x'):           self.h_act_on_highlighted,
                    curses.ascii.SP:    self.h_act_on_highlighted,
                    })


class BoxMultiLineAction(nps.BoxTitle):
    _contained_widget = MultiLineAction


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


class SaveMenu(nps.FormBaseNew):
    DEFAULT_LINES = 12
    DEFAULT_COLUMNS = 90
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        if self.parentApp.ses:
            path = self.parentApp.ses.path
            filename = "unknown.mtk"
            match = re.match("[a-zA-ZüÜöÖäÄ_\- ]+\.ptk", self.parentApp.ses.path)
            if match:
                filename = match.group(0)
        else:
            # TODO: Try on windows
            path = os.path.expanduser("~")
            filename = "session.ptk"

        self.title = self.add(nps.FixedText, rely=1, relx=3, value="Select the folder where the session should be saved:")
        self.path = self.add(nps.TitleFilename, rely=2, relx=3, name="Path:", value=path)
        self.filename = self.add(nps.TitleText, rely=3, relx=3, name="Filename:", value=filename)
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


class AddFun(nps.FormBaseNew):
    DEFAULT_LINES = 18
    DEFAULT_COLUMNS = 110
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.MultiLine, rely=1, relx=3, editable=False, values=["Enter your functions line by line, eg:", "\tf = cos(2*x+4) / exp(y)", "\tg = x**2 + z**(x + 2)"])
        self.to_add = self.add(AddBox, rely=4, relx=3, max_height=8, exit_right=True, scroll_exit=True)
        self.b_add = self.add(nps.ButtonPress, rely=13, relx=1, name="Add Functions", when_pressed_function=self.parentApp.switchFormPrevious)
        self.status = self.add(nps.FixedText, rely=15, relx=3, value="Press 'Enter' to start/stop writing in the textbox.")
        self.status.important = True  # makes it bold and green


class AddBox(nps.MultiLineEditableBoxed):

    def when_cursor_moved(self):
        self.parent.status.value += "Seems valid?"
        for line in self.values:
            if not sessions.check_valid_fun(line):
                self.parent.status.value = f"Invalid function: {line}"
        self.parent.status.update()

class MainSelect(nps.TitleSelectOne):
    def when_value_edited(self):
        self.parent.change_main()


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
        self.main_select = self.add(MainSelect, scroll_exit=True, rely=15, name="Select what do display:", values=["functions", "variables", "vectors"])
        self.pager = self.add(BoxMultiLineAction, editable=True, exit_left=True, scroll_exit=True, relx=20, rely=22, max_height=10, name="Hier steht zeug:", values=["alle", "meine", "entchen"])
        self.status = self.add(nps.Textfield, rely=MAXY - 2 - self.BLANK_LINES_BASE, relx=1, editable=False)

        self.command = self.add(nps.TextCommandBox, name="command box", rely=MAXY - 1 - self.BLANK_LINES_BASE, relx=0, )
        self.action_controller s= nps.ActionControllerSimple()


        # Todo: unnecessary lines?
        self.status.important = True    # makes it bold and green
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

    def change_main(self):
        if self.main_select.value == [0]:
            self.pager.values = self.parentApp.ses.get_funs()
            self.pager.name = "Functions"
        elif self.main_select.value == [1]:
            self.pager.values = self.parentApp.ses.get_vars()
            self.pager.name = "Values"
        elif self.main_select.value == [2]:
            self.pager.values = self.parentApp.ses.get_vecs()
            self.pager.name = "Vectors"
        self.pager.update()

    def call_import(self):
        self.parentApp.switchForm("import")

    def call_save(self):
        self.parentApp.switchForm("save")

    def call_add_fun(self):
        self.parentApp.switchForm("add_fun")


def save_session(session: sessions.PKTSession):
    return sessions.check_save_session(session)


def exit_app():
    if nps.notify_yes_no("Are you sure you want to exit Praktimatika?", title='Exit Praktimatika'):
        sys.exit()


def change_setting(setting, value):
    pass


class StartupMenu(nps.FormBaseNewWithMenus):
    def create(self):
        MAXY, MAXX = self.lines, self.columns
        self.title = self.add(nps.FixedText, name="Title", value=f"Welcome to Praktimatika:{MAXY, MAXX, self.BLANK_LINES_BASE}")
        self.select = self.add(nps.TitleSelectOne, scroll_exit=True, max_height=2, name='Load Session?', values=['No, create new session', 'Load PKTSession from file (.ptk)'])
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
            self.parentApp.ses = sessions.PKTSession(os.getcwd() + "new_session.ptk")
            self.parentApp.switchForm('home')
            self.status.value = "Status: Creating new session."
        # load session
        elif self.select.value == [1]:
            self.parentApp.ses = sessions.load_session(self.input_file.value)
            self.parentApp.switchForm('home')
            self.status.value = f"Status: Loading session from: {self.input_file.value}"
        else:
            self.status.value = "Status: Please select wether you want to load a session or create a new one and then press 'Start'."


class Praktimatika(nps.NPSAppManaged):
    """Managed Application. Contains the Praktimatika PKTSession, so that all forms and widgets can access it."""
    def onStart(self):
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
        # Add Menus
        add_fun = self.addForm("add_fun", AddFun, name="Add a function")


if __name__ == '__main__':
    TestApp = Praktimatika().run()













