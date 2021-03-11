#
# VECTOR MENU
#
class UserFuncMenu(nps.FormBaseNew):
    DEFAULT_LINES = 20
    DEFAULT_COLUMNS = 90
    SHOW_ATX = 8
    SHOW_ATY = 2

    def create(self):
        self.title = self.add(nps.FixedText, rely=1, relx=3, value="Select the action to perform on the function:")
        self.fun = self.add(nps.FixedText, rely=2, relx=3, value="None")
        self.options = self.add(twid.UserFuncAction, rely=5, relx=3)

        # self.status = self.add(nps.FixedText, rely=self.lines - 3, relx=3, value="")
        # self.status.important = True  # makes it bold and green

    def pre_edit_loop(self):
        self.fun.value = f"{self.parentApp.function[0]}={self.parentApp.function[1]}"
        self.fun.update()

    def dummy(self):
        nps.notify_confirm(f"{self.fun.value}: ")