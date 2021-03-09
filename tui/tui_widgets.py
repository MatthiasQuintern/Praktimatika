import npyscreen as nps
import curses
from tools import checks
from npyscreen import wgwidget as widget
from curses import ascii
import sympy as sy
#
# BASE WIDGETS
#
class CheckBox(nps.CheckBox):
    def h_select_exit(self, ch):
        self.h_toggle(ch)
        self.editing = False
        self.how_exited = widget.EXITED_DOWN


class Input(nps.TitleText):
    def __init__(self, screen, check_method=None, allow_none=False, invalid_message=None, give_status=True, begin_entry_at=16, field_width=None,
                 value=None, use_two_lines=False, hidden=False, labelColor='STANDOUT', allow_override_begin_entry_at=True, *args, **keywords):

        self.check_method = check_method    # method used to check if the input is valid
        self.allow_none = allow_none        # if nothing is a valid input
        self.valid_input = True
        if self.check_method is not None:
            if not self.check_method(value) and not (self.allow_none and (value == "" or value is None)):
                self.valid_input = False

        self.give_status = give_status
        if value is None:
            value = ""

        if invalid_message:
            self.invalid_message = invalid_message

        super(Input, self).__init__(screen, begin_entry_at=begin_entry_at, field_width=field_width, value=value, use_two_lines=use_two_lines, hidden=hidden, labelColor=labelColor,
                                    allow_override_begin_entry_at=allow_override_begin_entry_at, **keywords)

        self.invalid_message = f"Invalid input in '{self.name}'"

    def when_value_edited(self):
        """sets the valid_input attribute accoirding to the check_method"""
        self.valid_input = True
        if self.check_method is not None:
            if not self.check_method(self.value) and not (self.allow_none and (self.value == "" or self.value is None)):
                self.valid_input = False
                if self.give_status and hasattr(self.parent, "status"):
                    self.parent.status.value = self.invalid_message

    def update(self, clear=True):
        super(Input, self).update()
        self.when_value_edited()


class TitleAction(nps.MultiLineAction):
    _contained_widgets = nps.TitleText


#
# VECTOR WIDGETS
#
class VecSelect(nps.Autocomplete):
    """Widget to select vectors"""
    def __init__(self, *args, **keywords):
        super(VecSelect, self).__init__(*args, **keywords)
        self.editable = True

    def auto_complete(self, inpt):
        # self.value = "Hier könnte ihre Werbung stehen"

        for i in range(1):
            # initial vector list
            veclist = self.parent.parentApp.ses.get_dict("Vectors", only_name=True)
            # remove entries which do not start with self.value
            possibilities = list(filter(lambda vec: vec.startswith(self.value), veclist))
            if len(possibilities) is 0:
                # can't complete
                curses.beep()  # play "alarm" sound
                break

            # if one possibility, autocomplete
            elif len(possibilities) is 1:
                if self.value != possibilities[0]:
                    self.value = possibilities[0]
                    break

            self.value = possibilities[self.get_choice(possibilities)]
            break

        # set cursor to the end of the word
        self.cursor_position = len(self.value)


class TVecSelect(nps.TitleText):
    _entry_type = VecSelect


class VecDisplay(nps.MultiLineAction):
    """Display Vectors and call the save menu when a vector is clicked"""

    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.ppa = self.parent.parentApp
        self.scroll_exit = True
        self.exit_left = True
        self.exit_right = True

    def actionHighlighted(self, act_on_this, key_press):
        if checks.is_number_array(act_on_this):
            # calls the SaveVector Menu for the selected Vector
            self.ppa.add_vec.vector = act_on_this
            self.ppa.switchForm("save_vec")
        return

    def set_up_handlers(self):
        # define all keys on which the widget reacts
        super().set_up_handlers()
        self.handlers.update({
            curses.ascii.TAB: self.h_exit_down,
            # curses.KEY_DOWN:     self.h_exit_down,
            # curses.KEY_UP:       self.h_exit_up,
            curses.KEY_LEFT: self.h_exit_left,
            curses.KEY_RIGHT: self.h_exit_right,
            "^P": self.h_exit_up,
            "^N": self.h_exit_down,
            curses.ascii.ESC: self.h_exit_escape,
            curses.KEY_MOUSE: self.h_exit_mouse,
            curses.ascii.NL: self.h_act_on_highlighted,
            curses.ascii.CR: self.h_act_on_highlighted,
        })


class BVecDisplay(nps.BoxTitle):
    _contained_widget = VecDisplay


class SingleVecDisplay(nps.TitleFixedText):
    """Display Vector and call the save menu when it is clicked"""
    def __init__(self, screen, begin_entry_at=16, field_width=None,
                 value=None, use_two_lines=False, hidden=False, labelColor='STANDOUT', allow_override_begin_entry_at=True, *args, **keywords):

        super(SingleVecDisplay, self).__init__(screen, begin_entry_at=begin_entry_at, field_width=field_width, value=value, use_two_lines=use_two_lines, hidden=hidden, labelColor=labelColor,
                                               allow_override_begin_entry_at=allow_override_begin_entry_at, **keywords)
        self.vector = None
        self.ppa = self.parent.parentApp

    def set_up_handlers(self):
        self.handlers = {
            curses.ascii.NL: self.call_save_menu,
            curses.ascii.CR: self.call_save_menu,
            ord("s"): self.call_save_menu,
        }

    def call_save_menu(self, key):
        if checks.is_number_array(self.vector):
            # calls the SaveVector Menu for the selected Vector
            self.ppa.save_vec.vector = self.vector
            self.ppa.switchForm("save_vec")




#
# PLOT WIDGETS
#
class PlotList(nps.MultiLineAction):
    """
    Widget containing a tree-like list of figures, axes and plots and also
    options to create them
    Clicking on one opens the tui_plot settings form by calling its load_settings(names) method
    """
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.ppa = self.parent.parentApp
        self.scroll_exit = True
        self.exit_left = True
        self.exit_right = True

    def actionHighlighted(self, act_on_this, key_press):
        fig, ax, pl = self.get_fig_ax_pl()
        # figure menu
        if "\u250f" in act_on_this:
            # if delete figure
            if key_press == curses.ascii.DEL or key_press == ord("d"):
                if nps.notify_yes_no(f"Delete {fig}?"):
                    try:
                        self.ppa.ses.figs.pop(fig)
                    except KeyError:
                        pass
            else:
                self.ppa.pl_fig.load_settings(fig, cursor_line=self.cursor_line)

        # axis
        elif "\u2523\u2533" in act_on_this:
            # if delete figure
            if key_press == curses.ascii.DEL or key_press == ord("d"):
                if nps.notify_yes_no(f"Delete {ax}?"):
                    try:
                        self.ppa.ses.figs[fig]["axes"].pop(ax)
                    except KeyError:
                        pass
            else:
                self.ppa.pl_ax.load_settings(fig, ax, cursor_line=self.cursor_line)
        # plots
        elif "\u2503\u2523\u2501" in act_on_this:
            # if delete figure
            if key_press == curses.ascii.DEL or key_press == ord("d"):
                if nps.notify_yes_no(f"Delete {pl}?"):
                    try:
                        self.ppa.ses.figs[fig]["axes"][ax]["plots"].pop(pl)
                    except KeyError:
                        pass
            else:
                self.ppa.pl_pl.load_settings(fig, ax, pl, cursor_line=self.cursor_line)

        # add figure
        elif act_on_this == "\u2505add figure":
            self.ppa.pl_fig.load_settings(f"figure{len(self.ppa.ses.figs)}", cursor_line=self.cursor_line)
        # add axis
        elif act_on_this == "\u2523\u2505add axis":
            self.ppa.pl_ax.load_settings(fig, f"axis{len(self.ppa.ses.figs[fig]['axes'])}", cursor_line=self.cursor_line)
        # add plot
        elif act_on_this == "\u2503\u2523\u2505add plot":
            self.ppa.pl_pl.load_settings(fig, ax, f"plot{len(self.ppa.ses.figs[fig]['axes'][ax]['plots'])}", cursor_line=self.cursor_line)


    def set_up_handlers(self):
        # define all keys on which the widget reacts
        super().set_up_handlers()
        self.handlers.update({
            curses.ascii.TAB: self.h_exit_down,
            # curses.KEY_DOWN:     self.h_exit_down,
            # curses.KEY_UP:       self.h_exit_up,
            curses.KEY_LEFT: self.h_exit_left,
            curses.KEY_RIGHT: self.h_exit_right,
            "^P":               self.h_exit_up,
            "^N":               self.h_exit_down,
            curses.ascii.ESC: self.h_exit_escape,
            curses.KEY_MOUSE: self.h_exit_mouse,
            curses.ascii.NL: self.h_act_on_highlighted,
            curses.ascii.CR: self.h_act_on_highlighted,
            curses.ascii.DEL: self.h_act_on_highlighted,
            ord("d"):        self.h_act_on_highlighted,
        })

    def update(self, clear=True):
        super().update()
        # update/create menu
        self.values = []
        for fig in self.ppa.ses.figs:
            self.values.append(f"\u250f{fig}")
            for ax in self.ppa.ses.figs[fig]["axes"]:
                self.values.append(f"\u2523\u2533{ax}")
                for pl in self.ppa.ses.figs[fig]["axes"][ax]["plots"]:
                    self.values.append(f"\u2503\u2523\u2501{pl}")
                self.values.append("\u2503\u2523\u2505add plot")
            self.values.append("\u2523\u2505add axis")
        self.values.append("\u2505add figure")

    def get_fig_ax_pl(self):
        # returns at which fig and ax and pl the cursor is
        fig = ax = pl = None
        for i in range(self.cursor_line + 1):
            if "\u250f" in self.values[i]:
                fig = self.values[i].replace("\u250f", "")  # get name
            elif "\u2523\u2533" in self.values[i]:
                ax = self.values[i].replace("\u2523\u2533", "")
            elif "\u2503\u2523\u2501" in self.values[i]:
                pl = self.values[i].replace("\u2503\u2523\u2501", "")
        return fig, ax, pl


class TBPlotList(nps.BoxTitle):
    _contained_widget = PlotList


#
# FUNCTION WIDGETS
#
class UserFuncAction(nps.MultiLineAction):
    """Widget containing actions to perform on functions"""
    def __init__(self, *args, **keywords):
        super(UserFuncAction, self).__init__(*args, **keywords)
        self.ppa = self.parent.parentApp
        self.actions = {
            "Calculate":            (self.ppa.switchForm, "m_fun_calc"),
            "Output Latex":         (self.ppa.output, sy.latex(self.ppa.function[1])),
            "Output Function":      (self.ppa.output, str(self.ppa.function[1])),
            "Error Propagation":    (self.ppa.switchForm, "error_prop"),
            "Delete":               (self.delete_fun, None),
            "Go Back":              (self.ppa.switchForm, "home")
        }
        self.values = list(self.actions.keys())

    def actionHighlighted(self, act_on_this, key_press):
        # nps.notify_confirm(f"{act_on_this, key_press}")
        # function(arg) as defined in self.actions
        self.actions[act_on_this][0](self.actions[act_on_this][1])

    def set_up_handlers(self):
        # copied from wgmultiline.py
        super().set_up_handlers()
        # define all keys on which the widget reacts
        self.handlers.update({
                        ord('l'):           self.h_act_on_highlighted,
                        ord('x'):           self.h_act_on_highlighted,
                        curses.ascii.NL:    self.h_act_on_highlighted,
                    })


    def output_latex(self):
        self.ppa.output(f"{self.ppa.function[0]}={sy.printing.latex(self.ppa.function[1], fold_short_frac=False, mul_symbol='dot', decimal_separator=self.ppa.dec_sep)}")

    def output_func(self):
        self.ppa.output(str(self.ppa.function[1]))

    def delete_fun(self, none):
        if nps.notify_yes_no("Do you really want to delete the function?"):
            self.ppa.ses.funs.pop(self.ppa.function[0])