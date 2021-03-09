import npyscreen as nps
import curses

#
# HOME MENU
#
class MultiLineAction(nps.MultiLineAction):
    """Main Widget in the home screen, to display functions, vectors, variables etc..."""
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.ppa = self.parent.parentApp

    def actionHighlighted(self, act_on_this, key_press):
        # set parentApp.function/vector/constant/variable to act_on_this
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
            self.ppa.vector = (name, self.ppa.ses.vecs[name])
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
        self.b_import = self.add(nps.ButtonPress, rely=8, relx=3, name="Import spreadsheet", when_pressed_function=self.call_import)
        self.b_save = self.add(nps.ButtonPress, rely=9, relx=3, name="Save Session", when_pressed_function=self.call_save)
        self.b_add_fun = self.add(nps.ButtonPress, rely=10, relx=3, name="Add Function", when_pressed_function=self.call_add_fun)
        self.b_add_vec = self.add(nps.ButtonPress, rely=11, relx=3, name="Add Vector", when_pressed_function=self.call_add_vec)
        self.b_weight = self.add(nps.ButtonPress, rely=18, relx=3, name="Weighted Median", when_pressed_function=self.call_weighted_median)
        self.b_latex = self.add(nps.ButtonPress, rely=19, relx=3, name="Latex Table", when_pressed_function=self.call_latex_table)
        self.b_plot = self.add(nps.ButtonPress, rely=20, relx=3, name="Plots", when_pressed_function=self.call_plot_menu)

        self.main_select = self.add(MainSelect, begin_entry_at=0, scroll_exit=True, rely=25, relx=3, max_height=5, max_width=30, name="Select what do display:", value=[0],
                                    values=["Functions", "Variables", "Vectors", "Constants"])
        self.main = self.add(BoxMultiLineAction, editable=True, exit_left=True, scroll_exit=True, relx=35, rely=25, max_height=10, name="Hier steht zeug:",
                             values=["alle", "meine", "entchen"])

        self.status = self.add(nps.Textfield, rely=MAXY - 2 - self.BLANK_LINES_BASE, relx=1, editable=False)
        self.status.important = True  # makes it bold and green

        self.command = self.add(nps.TextCommandBox, name="command box", rely=MAXY - 1 - self.BLANK_LINES_BASE, relx=0, )
        self.action_controller = nps.ActionControllerSimple()


        # Todo: unnecessary lines?

        self.nextrely = 2

        self.status.value = 'Command Line:'

        # OWN STUFF
        self.mmenu = self.new_menu(name="Select Theme:", shortcut="^M")  # Todo: shortcut not working
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
        self.m_save.addItem("Quicksave", self.parentApp.ses.check_save_session)

    def pre_edit_loop(self):
        # main box
        self.change_main()

    def change_main(self):
        if self.main_select.value:
            name = self.main_select.values[self.main_select.value[0]]
            self.main.values = self.parentApp.ses.get_dict(name)
            self.main.name = name

        self.main.update()

    def call_import(self):
        self.parentApp.switchForm("import")

    def call_save(self):
        self.parentApp.switchForm("save")

    def call_add_fun(self):
        self.parentApp.switchForm("add_fun")

    def call_add_vec(self):
        self.parentApp.switchForm("add_vec")

    def call_weighted_median(self):
        self.parentApp.switchForm("weighted_median")

    def call_latex_table(self):
        self.parentApp.switchForm("latex_table")

    def call_plot_menu(self):
        # create default figure if there is none
        if len(self.parentApp.ses.figs) == 0:
            self.parentApp.pl_fig.load_settings("figure0", switch_to_form=False)
        else:
            nps.notify_confirm(f"{self.parentApp.ses.figs.keys()}")
        self.parentApp.switchForm("pl_fig")

