import npyscreen as nps
import curses
from tui import tui_widgets as twid

#
# HOME MENU
#
class MultiLineAction(nps.MultiLineAction):
    """Main Widget in the home screen, to display functions, vectors, variables etc..."""
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.ppa = self.parent.parentApp

    def actionHighlighted(self, act_on_this, key_press):
        # set parentApp.function/array/constant/variable to act_on_this
        # values=["Functions", "Variables", "Vectors", "Constants"]
        # nps.notify_confirm(f"{act_on_this},  {key_press}")
        # act_on_this is a name=value string
        name, value = act_on_this.split("=")
        if self.parent.main_select.value == [0]:    # Function
            # self.ppa.function = (name, self.ppa.ses.funs[name])
            self.ppa.function = (name, self.ppa.ses.funs[name])
            self.ppa.switchForm("m_fun")
        elif self.parent.main_select.value == [1]:    # Variable
            self.ppa.variable = (name, self.ppa.ses.vals[name])
        elif self.parent.main_select.value == [2]:    # Vector
            self.ppa.array = (name, self.ppa.ses.arrs[name])
        elif self.parent.main_select.value == [3]:    # Constant
            self.ppa.constant = (name, self.ppa.ses.consts[name])
        return



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
                        curses.ascii.NL:    self.h_act_on_highlighted,
                        curses.ascii.CR:    self.h_act_on_highlighted,
                        curses.ascii.SP:    self.h_act_on_highlighted,

                    })


class BoxMultiLineAction(nps.BoxTitle):
    _contained_widget = MultiLineAction
    def __init__(self, *args, **keywords):
        self.how_exited = False
        super(BoxMultiLineAction, self).__init__(*args, **keywords)

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
        bcol1 = 1
        col1 = 3
        col2 = 35
        wcol1 = col2 - col1
        y0 = 1
        y1 = y0 + 3     # Select, Main
        y2 = y1 + 7     # Add Buttons
        y3 = y2 + 3     # Tools
        y4 = y3 + 5     # Save
        y5 = y4 + 3     # Settings

        self.t_welcome = self.add(nps.FixedText, rely=y0, relx=col1, editable=False, value=f"Welcome to Praktimatika!")

        # DISPLAY SELECT
        self.line1 = self.add(nps.FixedText, rely=y1, relx=col1, editable=False, value="\u2501" * 300)
        self.main_select = self.add(MainSelect, begin_entry_at=0, scroll_exit=True, rely=y1 + 1, relx=col1, max_height=5, max_width=30, name="Select what do display:", value=[0],
                                    values=["Functions", "Variables", "Arrays", "Constants"])
        # ADD Buttons
        self.line2 = self.add(nps.FixedText, rely=y2, relx=col1, editable=False, value="\u2501" * wcol1)
        self.b_add_fun = self.add(nps.ButtonPress, rely=y2 + 1, relx=bcol1, name="Add Function", when_pressed_function=self.call_add_fun)
        self.b_add_vec = self.add(nps.ButtonPress, rely=y2 + 2, relx=bcol1, name="Add Array", when_pressed_function=self.call_add_vec)

        # TOOL Buttons
        self.line3 = self.add(nps.FixedText, rely=y3, relx=col1, editable=False, value="\u2501" * wcol1)
        self.b_import = self.add(nps.ButtonPress, rely=y3+1, relx=bcol1, name="Import Arrays From Spreadsheet", when_pressed_function=self.call_import)
        self.b_weight = self.add(nps.ButtonPress, rely=y3 + 2, relx=bcol1, name="Weighted Median", when_pressed_function=self.call_weighted_median)
        self.b_latex = self.add(nps.ButtonPress, rely=y3 + 3, relx=bcol1, name="Latex Table", when_pressed_function=self.call_latex_table)
        self.b_plot = self.add(nps.ButtonPress, rely=y3 + 4, relx=bcol1, name="Plots", when_pressed_function=self.call_plot_menu)

        # SAVE Buttons
        self.line4 = self.add(nps.FixedText, rely=y4, relx=col1, editable=False, value="\u2501" * wcol1)
        self.b_save = self.add(nps.ButtonPress, rely=y4 + 1, relx=bcol1, name="Save Session", when_pressed_function=self.parentApp.quicksave)
        self.b_save_as = self.add(nps.ButtonPress, rely=y4 + 2, relx=bcol1, name="Save Session As", when_pressed_function=self.call_save)

        # SETTINGS
        self.line5 = self.add(nps.FixedText, rely=y5, relx=col1, editable=False, value="\u2501" * wcol1)
        self.b_settings = self.add(nps.ButtonPress, rely=y5 + 1, relx=bcol1, name="Settings", when_pressed_function=self.call_settings)

        # MAIN DISPLAY
        maxh = MAXY - 5 - self.BLANK_LINES_BASE - y1 - 1
        self.main = self.add(BoxMultiLineAction, editable=True, exit_left=True, scroll_exit=True, rely=y1 + 1, relx=col2, max_height=maxh, name="Display",
                             values=[""])


        self.line6 = self.add(nps.FixedText, rely=MAXY - 5 - self.BLANK_LINES_BASE, relx=col1, editable=False, value="\u2501" * 300)
        self.shortcuts = self.add(nps.TitleMultiLine, name="Shortcuts:", begin_entry_at=15, max_height=2, rely=MAXY - 4 - self.BLANK_LINES_BASE, relx=3, editable=False,
                                  values=["(f/a/c): Show (Functions/Arrays/Constants), (F/A/C) Jump to (Functions/Arrays/Constants)",
                                        "i: Import, m: Weighted Median, t: Latex Table, p: Plots"])

        self.status = self.add(nps.Textfield, rely=MAXY - 2 - self.BLANK_LINES_BASE, relx=3, editable=False, value="Command Line (not working yet)")
        self.status.important = True  # makes it bold

        self.command = self.add(nps.TextCommandBox, name="command box", rely=MAXY - 1 - self.BLANK_LINES_BASE, relx=3, )
        self.action_controller = nps.ActionControllerSimple()

        """self.mmenu = self.new_menu(name="Select Theme:", shortcut="^M")  # Todo: shortcut not working
        self.mmenu.addItemsFromList([("Light Font", self.parentApp.change_setting, None, None, ("theme", nps.Themes.TransparentThemeLightText)),
                                     ("Dark Font", self.parentApp.change_setting, None, None, ("theme", nps.Themes.TransparentThemeDarkText)),
                                     ("Default", self.parentApp.change_setting, None, None, ("theme", nps.Themes.DefaultTheme)),
                                     ("Colourful", self.parentApp.change_setting, None, None, ("theme", nps.Themes.ColorfulTheme)),
                                     ("Elegant", self.parentApp.change_setting, None, None, ("theme", nps.Themes.ElegantTheme))])

        self.m_quit = self.new_menu(name="Save and Quit Menu", shortcut="^S")  # Todo: shortcut not working
        self.m_quit.addItemsFromList([("Save", self.parentApp.ses.check_save_session),
                                     ("Save As", self.parentApp.switchForm, None, None, ("save",)),
                                     ("Quit without Saving", self.parentApp.exit_app, None, None, None)])

        self.m_save = self.new_menu(name="Quicksave PKTSession")
        self.m_save.addItem("Quicksave", self.parentApp.ses.check_save_session)"""

    def set_up_handlers(self):
        self.complex_handlers = []
        self.handlers = {
            curses.KEY_F1:  self.h_display_help,
            "KEY_F(1)":     self.h_display_help,
            "^O":           self.h_display_help,
            "^L":           self.h_display,
            curses.KEY_RESIZE: self._resize,
            # change main display
            ord("f"):       self.change_main,
            ord("a"):       self.change_main,
            ord("c"):       self.change_main,
            ord("F"):       self.change_main,
            ord("A"):       self.change_main,
            ord("C"):       self.change_main,
            # open forms
            ord("i"):       self.call_import,
            ord("m"):       self.call_weighted_median,
            ord("t"):       self.call_latex_table,
            ord("p"):       self.call_plot_menu,
        }

    def pre_edit_loop(self):
        # main box
        self.change_main()

    def change_main(self, key=0, jump=False):
        # wehere to jump for which key
        keys = {
            ord("f"):   0,
            ord("F"):   0,
            ord("a"):   2,
            ord("A"):   2,
            ord("c"):   3,
            ord("C"):   3,
        }
        if key > 0:
            try:
                self.main_select.value = [keys[key]]
                # for capital letters, set jump to true
                if 65 <= key <= 97:
                    jump = True
            except KeyError:
                pass

        if self.main_select.value:
            name = self.main_select.values[self.main_select.value[0]]
            self.main.values = self.parentApp.ses.get_dict(name)
            self.main.name = name
        if jump:
            self.set_editing(self.main)
        self.main.update()
        self.main_select.update()

    def call_import(self, *args):
        self.parentApp.switchForm("import")

    def call_save(self, *args):
        self.parentApp.switchForm("save")

    def call_settings(self, *args):
        self.parentApp.switchForm("settings")

    def call_add_fun(self, *args):
        self.parentApp.switchForm("add_fun")

    def call_add_vec(self, *args):
        self.parentApp.switchForm("add_arr")

    def call_weighted_median(self, *args):
        self.parentApp.switchForm("weighted_median")

    def call_latex_table(self, *args):
        self.parentApp.switchForm("latex_table")

    def call_plot_menu(self, *args):
        # create default figure if there is none
        if len(self.parentApp.ses.figs) == 0:
            self.parentApp.pl_fig.load_settings("figure0", switch_to_form=False)
        else:
            nps.notify_confirm(f"{self.parentApp.ses.figs.keys()}")
        self.parentApp.switchForm("pl_fig")


class Settings(twid.BaseForm):
    def create(self):
        col1 = 3
        bcol1 = col1 -2
        y0 = 1
        y1 = y0 + 4
        y2 = y1 + 4
        y3 = y2 + 5
        y4 = y3 + 8
        self.title = self.add(nps.MultiLine, rely=y0, relx=col1, editable=False,
                              values=["Change the Praktimatika Settings", "Settings are stored in 'praktimatika.conf'"])

        self.line0 = self.add(nps.FixedText, rely=y1, relx=col1, editable=False, value="\u2501" * 300)
        self.i_dec_sep = self.add(twid.Input, rely=y1+1, relx=col1, name="Decimal Separator:", begin_entry_at=20)
        self.t_dec_sep = self.add(nps.FixedText, rely=y1+2, relx=col1, editable=False, value="This option only affects the output of Latex Tables")


        self.line1 = self.add(nps.FixedText, rely=y2, relx=col1, editable=False, value="\u2501" * 300)
        self.t_output = self.add(nps.FixedText, rely=y2+1, relx=col1, editable=False, value="These options affect the output of things, eg. LaTeX tables or functions")
        self.c_copy_clip = self.add(twid.CheckBox, rely=y2+2, relx=3, editable=True, name="Copy output to system clipboard")
        self.c_print_file = self.add(twid.CheckBox, rely=y2+3, relx=3, editable=True, name="Print output to 'outout.txt'")

        self.line2 = self.add(nps.FixedText, rely=y3, relx=col1, editable=False, value="\u2501" * 300)
        self.theme = self.add(nps.TitleSelectOne, rely=y3+1, relx=col1, scroll_exit=True, max_height=6, name="Theme", values=list(self.parentApp.themes.keys()))
        self.t_output = self.add(nps.FixedText, rely=y3 + 7, relx=col1, editable=False, value="Theme changes will be applied after restart")

        self.line3 = self.add(nps.FixedText, rely=y4, relx=col1, editable=False, value="\u2501" * 300)
        self.b_ok = self.add(nps.ButtonPress, rely=y4+1, relx=1, name="Ok", when_pressed_function=self.save_quit)
        self.b_apply = self.add(nps.ButtonPress, rely=y4+1, relx=5, name="Apply", when_pressed_function=self.save)
        self.b_cancel = self.add(nps.ButtonPress, rely=y4+1, relx=13, name="Cancel", when_pressed_function=self.parentApp.switchFormPrevious)

        # self.status = self.add(nps.FixedText, rely=16, relx=3, editable=False, value="Press 'Enter' to start/stop writing in the textbox.")
        # self.status.important = True  # makes it bold and green


    def save_quit(self):
        self.save()
        self.parentApp.switchFormPrevious()

    def save(self):
        # update the settings dict and call save_settings method, to write settings in file
        self.parentApp.settings["dec_sep"] = self.i_dec_sep.value
        self.parentApp.settings["print_output"] = self.c_print_file.value
        self.parentApp.settings["copy_clip"] = self.c_copy_clip.value
        self.parentApp.settings["theme"] = self.theme.values[self.theme.value[0]]
        self.parentApp.save_settings()

    def pre_edit_loop(self):
        # load the current settings
        settings = self.parentApp.settings
        self.i_dec_sep.value = settings["dec_sep"]
        self.c_print_file.value = settings["print_output"]
        self.c_copy_clip.value = settings["copy_clip"]
        if settings["theme"] in self.theme.values:
            self.theme.value = [self.theme.values.index(settings["theme"])]
        else:
            self.theme.value = [0]

