import npyscreen as nps
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from tools import checks
from tui import tui_widgets as twid
from curses import ascii


#
# Base Form for the plot menus
#
class PltMenu(twid.BaseForm):
    col1 = 25
    col2 = 58
    def create(self):
        col1 = PltMenu.col1
        # "shortcut"
        self.figsd = self.parentApp.ses.figs
        self.list = self.add(twid.TBPlotList, rely=2, relx=3, name="Figures", max_width=20, editable=True)
        self.shortcuts = self.add(nps.FixedText, rely=self.lines - 4, relx=col1, editable=False, value="Shortcuts: f: Jump to Figures Menu")
        self.status = self.add(nps.FixedText, rely=self.lines - 3, relx=col1, editable=False, value="Plot Menu")
        self.status.important = True  # makes it bold and green

        self.add_handlers({
            "^K":             self.to_figures,
            ord("f"):         self.to_figures,
        })

    def back_to_home(self):
        self.parentApp.switchForm("home")

    def save(self):
        pass

    def pre_edit_loop(self):
        self.list.update()

    def to_figures(self, *args):
        self.exit_editing()
        self.set_editing(self.list)

        self.display()


#
# PLOT MAIN MENU
#
class FigMenu(PltMenu):

    def create(self):
        super(FigMenu, self).create()
        col1 = PltMenu.col1
        col2 = PltMenu.col2
        y0 = 6
        y1 = 3 + y0
        y2 = 3 + y1
        # "shortcut"
        self.figname = ""
        self.desc_1 = self.add(nps.MultiLine, rely=2, relx=col1, max_height=5, editable=False,
                               values=["Change figure settings below and press 'Save' to add it to your session.",
                                       "After that, you can added axes in the menu on the left and then the plot data.",
                                       "Press 'Show Plot' to show the plot in the matplotlib interactive window.",
                                       "To save the figure as image-file, press 'Save Image' or save it from the matplotlib interactive window"])

        self.line0 = self.add(nps.FixedText, rely=y0, relx=col1, editable=False, value="\u2501" * 200)
        self.b_save = self.add(nps.ButtonPress, rely=y0 + 1, relx=col1-2, name="Save", when_pressed_function=self.save)
        self.i_name = self.add(twid.Input, rely=y0 + 2, relx=col1, name="figure name:", value="figure", check_method=checks.is_name)

        self.line1 = self.add(nps.FixedText, rely=y1, relx=col1, editable=False, value="\u2501" * 200)
        # BUTTONS
        self.b_plot = self.add(nps.ButtonPress, rely=y1 + 1, relx=col1-2, name="Show Plot", when_pressed_function=self.show)
        self.b_imsave = self.add(nps.ButtonPress, rely=y1 + 2, relx=col1-2, name="Save Image", when_pressed_function=self.imsave)

        self.line2 = self.add(nps.FixedText, rely=y2, relx=col1, editable=False, value="\u2501" * 200)
        # SETTINGS
        self.i_figsize = self.add(twid.Input, rely=y2 + 1, relx=col1, name="figsize")
        self.i_dpi = self.add(twid.Input, rely=y2 + 2, relx=col1, name="dpi", check_method=checks.is_int, allow_none=True)
        self.c_constr = self.add(twid.CheckBox, rely=y2 + 3, relx=col1, name="Constrained Layout", value=[0], scroll_exit=True, field_width=30)
        self.c_tight = self.add(twid.CheckBox, rely=y2 + 4, relx=col1, name="Tight Layout", value=[0], scroll_exit=True, field_width=30)

        self.b_back = self.add(nps.ButtonPress, rely=y2 + 5, relx=col1-2, name="Go Back", when_pressed_function=self.back_to_home)


    def save(self):
        for inp in [self.i_name, self.i_figsize, self.i_dpi]:
            if not inp.valid_input:
                nps.notify_confirm(f"Could not save figure settings: Invalid input in '{inp.name}'")
                return
        # check if name was changed
        if not self.figname == self.i_name.value:
            try:
                self.parentApp.ses.figs[self.i_name.value] = self.parentApp.ses.figs.pop(self.figname)
            except KeyError:
                pass
        # get axes if figure already exists, otherwise axes dict will be lost
        try:
            axes = self.parentApp.ses.figs[self.i_name.value]["axes"]
        except KeyError:
            axes = {}
        self.status.value = self.parentApp.ses.add_fig(self.i_name.value,
                                                       figsize=self.i_figsize.value, dpi=self.i_dpi.value,
                                                       tight_layout=self.c_tight.value, constrained_layout=self.c_constr.value,
                                                       axes=axes)
        self.list.update()
        self.status.update()
        self.display()

    def imsave(self):
        if self.i_name.value in self.parentApp.ses.figs:
            fig = self.parentApp.ses.create_fig(self.i_name.value)
            if isinstance(fig, Figure):
                fig.savefig("Mein Plot!")
            else:
                if isinstance(fig, BaseException):
                    self.parentApp.show_error("Error saving figure", fig)
        else:
            nps.notify_confirm(f"Error saving figure: '{self.i_name.value}' not in session figures")

    def show(self):
        if self.i_name.value in self.parentApp.ses.figs:
            fig = self.parentApp.ses.create_fig(self.i_name.value)
            if isinstance(fig, Figure):
                plt.show(block=False)
            else:
                if isinstance(fig, BaseException):
                    self.parentApp.show_error("Error showing figure", fig)
        else:
            nps.notify_confirm(f"Error showing figure: '{self.i_name.value}' not in session figures")

    def load_settings(self, figname: str, switch_to_form=True, cursor_line=0):
        """loads settings from session figs dict if possible. if not creates new with defaults"""
        # update, because it will be empty at loading
        self.figsd = self.parentApp.ses.figs
        self.list.cursor_line = cursor_line
        self.figname = figname
        self.i_name.value = figname
        if figname in self.figsd:
            self.c_tight.value = self.figsd[figname]["constrained_layout"]
            self.c_constr.value = self.figsd[figname]["tight_layout"]
            self.i_dpi.value = str(self.figsd[figname]["dpi"])
            self.i_figsize.value = str(self.figsd[figname]["figsize"])
        else:
            # create defaults
            self.c_tight.value = False
            self.c_constr.value = False
            self.i_dpi.value = "300"
            self.i_figsize.value = ""
            # create default axes and plot
            self.save()
            self.parentApp.pl_ax.load_settings(self.figname, "axes0", switch_to_form=False)
            self.parentApp.pl_pl.load_settings(self.figname, "axes0", "plot0", switch_to_form=False)
        if switch_to_form:
            self.parentApp.switchForm("pl_fig")


class AxesMenu(PltMenu):
    # DEFAULT_LINES = 25
    # DEFAULT_COLUMNS = 110
    # SHOW_ATX = 8
    # SHOW_ATY = 2

    def create(self):
        super(AxesMenu, self).create()
        col1 = PltMenu.col1
        col2 = 58
        y0 = 6
        y1 = y0 + 3
        y2 = y1 + 6
        y3 = y2 + 5

        self.figname = ""
        self.axname = ""
        self.desc_1 = self.add(nps.MultiLine, rely=2, relx=col1, max_height=4, editable=False, values=["Change axes settings below and press 'Save' to add it to the figure .",
                                                                                                       "After that, you can added axes in the menu on the left and then the plot data.",
                                                                                                       "Press 'Show Plot' to show the plot in the matplotlib interactive window.",
                                                                                                       "To save the figure as image-file, press 'Save Image' or save it from the matplotlib interactive window"])
        self.line0 = self.add(nps.FixedText, rely=y0, relx=col1, editable=False, value="\u2501" * 200)
        self.b_save = self.add(nps.ButtonPress, rely=y0+1, relx=col1-2, name="Save", when_pressed_function=self.save)
        # self.b_save_as = self.add(nps.ButtonPress, rely=4, relx=1, name="Save as", when_pressed_function=exit_app)
        self.i_name = self.add(twid.Input, rely=y0 + 2, relx=col1, name="axis name:", value="axis", check_method=checks.is_name)

        self.line1 = self.add(nps.FixedText, rely=y1, relx=col1, editable=False, value="\u2501" * 200)
        # LABEL, TITLE
        self.i_title = self.add(twid.Input, rely=y1 + 1, relx=col1, name="title:")
        self.i_xlabel = self.add(twid.Input, rely=y1 + 2, relx=col1, name="x-label:")
        self.i_ylabel = self.add(twid.Input, rely=y1 + 3, relx=col1, name="y-label:")
        self.i_fontsize = self.add(twid.Input, rely=y1 + 4, relx=col1, name="fontsize:", check_method=checks.is_int, allow_none=True)
        # LEGEND
        # self.s_legend = self.add(nps.TitleSelectOne, rely=y1, relx=col2, name="legend", value=[0], values=[""], scroll_exit=True, max_height=5, field_width=30)
        self.c_legend = self.add(nps.CheckBox, rely=y1 + 5, relx=col1, name="legend", value=[0], scroll_exit=True, field_width=30)

        self.line2 = self.add(nps.FixedText, rely=y2, relx=col1, editable=False, value="\u2501" * 200)
        # LIMITS
        self.i_uxlim = self.add(twid.Input, rely=y2 + 1, relx=col1, name="x-upper-limit:", check_method=checks.is_number, allow_none=True, field_width=30)
        self.i_lxlim = self.add(twid.Input, rely=y2 + 2, relx=col1, name="x-lower-limit:", check_method=checks.is_number, allow_none=True, field_width=30)
        self.i_uylim = self.add(twid.Input, rely=y2 + 1, relx=col2, name="y-upper-limit:", check_method=checks.is_number, allow_none=True, field_width=30)
        self.i_lylim = self.add(twid.Input, rely=y2 + 2, relx=col2, name="y-lower-limit:", check_method=checks.is_number, allow_none=True, field_width=30)
        # SCALES
        self.s_xscale = self.add(nps.TitleSelectOne, rely=y2 + 3, relx=col1, name="x-scale:", value=[0], values=["linear", "log"], scroll_exit=True, max_height=2, field_width=30,
                                 labelColor='STANDOUT')
        self.s_yscale = self.add(nps.TitleSelectOne, rely=y2 + 3, relx=col2, name="y-scale:", value=[0], values=["linear", "log"], scroll_exit=True, max_height=2, field_width=30,
                                 labelColor='STANDOUT')

        self.line3 = self.add(nps.FixedText, rely=y3, relx=col1, editable=False, value="\u2501" * 200)
        # GRID
        self.s_grid = self.add(nps.TitleSelectOne, rely=y3 + 1, relx=col1, name="grid style:", value=[0], values=["major", "minor", "both", "none"], scroll_exit=True, max_height=4,
                               field_width=30, labelColor='STANDOUT')
        self.s_grid_line = self.add(nps.TitleSelectOne, rely=y3 + 1, relx=col2, name="grid line:", value=[0], values=["-", "--", "-.", ":"], scroll_exit=True, max_height=5,
                                    field_width=30, labelColor='STANDOUT')
        self.i_grid_color = self.add(twid.Input, rely=y3 + 5, relx=col1, name="grid color:", check_method=None, allow_none=True, field_width=30)

        self.b_back = self.add(nps.ButtonPress, rely=y3 + 6, relx=col1-2, name="Go Back", when_pressed_function=self.back_to_home)


    def save(self):
        for inp in [self.i_name, self.i_title, self.i_xlabel, self.i_ylabel, self.i_fontsize, self.i_uxlim, self.i_lxlim, self.i_uylim, self.i_lylim, self.i_grid_color]:
            if not inp.valid_input:
                nps.notify_confirm(f"Could not save axis settings: Invalid in putin '{inp.name}'")
                return
        # check if name was changed
        if not self.axname == self.i_name.value:
            try:
                self.figsd[self.figname]["axes"][self.i_name.value] = self.figsd[self.figname]["axes"].pop(self.axname)
            except KeyError:
                pass
        try:
            plots = self.figsd[self.figname]["axes"][self.i_name.value]["plots"]
        except KeyError:
           plots = {}
        self.status.value = self.parentApp.ses.add_axes(self.figname, self.i_name.value, title=self.i_title.value, xlabel=self.i_xlabel.value, ylabel=self.i_ylabel.value,
                                    legend=self.c_legend.value, fontsize="13",
                                    grid=self.s_grid.values[self.s_grid.value[0]], gline=self.s_grid_line.values[self.s_grid_line.value[0]], gcolor=self.i_grid_color.value,
                                    xlim=(self.i_lxlim.value, self.i_uxlim.value), ylim=(self.i_lylim.value, self.i_uylim.value),
                                    xscale=self.s_xscale.values[self.s_xscale.value[0]], yscale=self.s_yscale.values[self.s_yscale.value[0]], plots=plots)
        self.list.update()
        self.status.update()
        self.display()

    def load_settings(self, figname: str, axname: str, switch_to_form=True, cursor_line=0):
        """loads settings from session figs dict if possible. if not creates new with defaults"""
        # update, because it will be empty at loading
        self.figsd = self.parentApp.ses.figs
        self.list.cursor_line = cursor_line
        self.figname = figname
        self.axname = axname
        self.i_name.value = axname
        if self.figname not in self.parentApp.ses.figs:
            nps.notify_confirm(f"Error loading axes menu: Figure {self.figname} does not exist\n{self.figsd}")
            return
        if axname in self.figsd[figname]["axes"]:
            d = self.figsd[figname]["axes"][axname]

            self.i_title.value = d["title"]
            self.i_xlabel.value = d["xlabel"]
            self.i_ylabel.value = d["ylabel"]
            # LIMITS
            self.i_uxlim.value = d["xlim"][1]
            self.i_lxlim.value = d["xlim"][0]
            self.i_uylim.value = d["ylim"][1]
            self.i_lylim.value = d["ylim"][0]
            # SCALES
            if d["xscale"] == "log":
                self.s_xscale.value = [1]
            else:
                self.s_xscale.value = [0]
            if d["yscale"] == "log":
                self.s_yscale.value = [1]
            else:
                self.s_yscale.value = [0]
            # GRID
            if d["grid"] in self.s_grid.values:
                self.s_grid.value = [self.s_grid.values.index(d["grid"])]
            else:
                self.s_grid.value = [0]
            if d["gline"] in self.s_grid_line.values:
                self.s_grid_line.value = [self.s_grid_line.values.index(d["gline"])]
            else:
                self.s_grid_line.value = [0]
            self.i_grid_color.value = d["gcolor"]

        else:
            # create defaults
            self.i_title.value = None
            self.i_xlabel.value = None
            self.i_ylabel.value = None
            # LIMITS
            self.i_uxlim.value = None
            self.i_lxlim.value = None
            self.i_uylim.value = None
            self.i_lylim.value = None
            # SCALES
            self.s_xscale.value = [0]
            self.s_yscale.value = [0]
            # GRID
            self.s_grid.value = [0]
            self.s_grid_line.value = [0]
            self.i_grid_color.value = "#777"
            self.save()
        if switch_to_form:
            self.parentApp.switchForm("pl_ax")


class PlotMenu(PltMenu):
    # TODO: plot functions, errorbars, hlines, vlines
    def create(self):
        super(PlotMenu, self).create()
        col1 = PltMenu.col1
        col2 = PltMenu.col2
        y0 = 4
        y1 = y0 + 3
        y2 = y1 + 3
        y3 = y2 + 5

        self.figname = "none"
        self.axname = "none"
        self.plname = "none"

        self.desc_1 = self.add(nps.MultiLine, rely=2, relx=col1, max_height=3, editable=False, values=["Select the x - and y-Data and change the settings to your liking.",
                                                                                                       "Press 'Plot' when done to show the plot."])
        self.line0 = self.add(nps.FixedText, rely=y0, relx=col1, editable=False, value="\u2501" * 200)
        self.b_save = self.add(nps.ButtonPress, rely=y0 + 1, relx=col1-2, name="Save", when_pressed_function=self.save)
        self.i_name = self.add(twid.Input, rely=y0 + 2, relx=col1, name="plot name:", value="plot", check_method=checks.is_name)

        self.line1 = self.add(nps.FixedText, rely=y1, relx=col1, editable=False, value="\u2501" * 200)
        # DATA
        self.xdata = self.add(twid.TArrSelect, rely=y1 + 1, relx=col1, name="x-Data (array)", use_two_lines=False, labelColor='STANDOUT')
        self.ydata = self.add(twid.TArrSelect, rely=y1 + 2, relx=col1, name="y-Data (array)", use_two_lines=False, labelColor='STANDOUT')

        self.line3 = self.add(nps.FixedText, rely=y2, relx=col1, editable=False, value="\u2501" * 200)
        # SETTINGS
        self.i_label = self.add(twid.Input, rely=y2 + 1, relx=col1, name="label:", value="label1", allow_none=True)
        self.i_color = self.add(twid.Input, rely=y2 + 2, relx=col1, name="Color:", field_width=30, allow_none=True)
        self.s_line = self.add(nps.TitleSelectOne, rely=y2 + 3, relx=col1, name="line:", value=[0], values=["none", "-", "--", "-.", ":"], scroll_exit=True, max_height=5,
                               field_width=30, labelColor='STANDOUT')
        self.s_marker = self.add(nps.TitleSelectOne, rely=y2 + 3, relx=col2, name="marker:", value=[0], scroll_exit=True, max_height=23, field_width=30, labelColor='STANDOUT',
                                 values=["none", ".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "s", "p", "*", "h", "H", "+", "D", "d", "|", "_"])

        self.b_back = self.add(nps.ButtonPress, rely=y3 + 8, relx=col1, name="Go Back", when_pressed_function=self.back_to_home)

    def save(self):
        for inp in [self.i_name, self.i_color]:
            if not inp.valid_input:
                nps.notify_confirm(f"Could not save plot settings: Invalid input in '{inp.name}'")
                return
        # check if name was changed
        if not self.plname == self.i_name.value:
            try:
                self.figsd[self.figname]["axes"][self.axname]["plots"][self.i_name.value] = self.figsd[self.figname]["axes"][self.axname]["plots"].pop(self.plname)
            except KeyError:
                pass

        self.status.value = self.parentApp.ses.add_plot(self.figname, self.axname, self.i_name.value, self.xdata.value, self.ydata.value, marker=self.s_marker.values[self.s_marker.value[0]],
                                    line=self.s_line.values[self.s_line.value[0]], color=self.i_color.value, label=self.i_label.value)
        self.status.update()
        self.list.update()
        self.display()

    def load_settings(self, figname: str, axname: str, plname: str, switch_to_form=True, cursor_line=0):
        """loads settings from session figs dict if possible. if not creates new with defaults"""
        # update, because it will be empty at loading
        self.figsd = self.parentApp.ses.figs
        self.list.cursor_line = cursor_line
        self.figname = figname
        self.axname = axname
        self.plname = plname
        self.i_name.value = plname
        if self.figname not in self.figsd:
            nps.notify_confirm(f"Error loading plot menu: Figure {figname} does not exist")
            return
        if self.axname not in self.figsd[figname]["axes"]:
            nps.notify_confirm(f"Error loading plot menu: Axis {axname} does not exist")
            return
        if plname in self.figsd[figname]["axes"][axname]["plots"]:
            d = self.figsd[figname]["axes"][axname]["plots"][plname]
            self.i_name.value = plname
            self.xdata.value = d["xdata"]
            self.ydata.value = d["ydata"]
            self.i_label.value = d["label"]
            self.i_color.value = d["color"]
            if d["marker"] in self.s_marker.values:
                self.s_marker.value = [self.s_marker.values.index(d["marker"])]
            else:
                self.s_marker.value = [0]
            if d["line"] in self.s_line.values:
                self.s_line.value = [self.s_line.values.index(d["line"])]
            else:
                self.s_line.value = [0]

        else:
            self.i_name.value = plname
            self.xdata.value = ""
            self.ydata.value = ""
            self.i_label.value = ""
            self.i_color.value = ""
            self.s_marker.value = [0]
            self.s_line.value = [1]
            self.save()
        if switch_to_form:
            self.parentApp.switchForm("pl_pl")
