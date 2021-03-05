import npyscreen as nps
import curses
import checks


class Input(nps.TitleText):
    def __init__(self, screen, check_method=None, invalid_message=None, valid_input=False, give_status=True, begin_entry_at=16, field_width=None,
                 value=None, use_two_lines=False, hidden=False, labelColor='STANDOUT', allow_override_begin_entry_at=True, **keywords):

        self.check_method = check_method    # method used to check if the input is valid
        self.invalid_message = f"Invalid input in '{self.name}'"
        self.valid_input = valid_input
        self.give_status = give_status
        if not hasattr(self.parent, "status"):
            self.give_status = False

        if invalid_message:
            self.invalid_message = invalid_message
        super().__init__(screen, begin_entry_at=begin_entry_at, field_width=field_width, value=value, use_two_lines=use_two_lines,
                         hidden=hidden, labelColor=labelColor, allow_override_begin_entry_at=allow_override_begin_entry_at, **keywords)

    def when_value_edited(self):
        """sets the valid_input attribute accoirding to the check_method"""
        self.valid_input = True
        if self.check_method:
            if not self.check_method(self.value):
                self.valid_input = False
                if self.give_status:
                    self.parent.status.value = self.invalid_message


class TitleAction(nps.MultiLineAction):
    _contained_widgets = nps.TitleText


class VecSelect(nps.Autocomplete):
    """Widget to select vectors"""

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
