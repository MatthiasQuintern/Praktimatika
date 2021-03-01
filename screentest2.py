"""#!/usr/bin/env python
import npyscreen


class ActionControllerSearch(npyscreen.ActionControllerSimple):
    def create(self):
        self.add_action('^/.*', self.set_search, True)

    def set_search(self, command_line, widget_proxy, live):
        self.parent.value.set_filter(command_line[1:])
        self.parent.wMain.values = self.parent.value.get()
        self.parent.wMain.display()


class FmSearchActive(npyscreen.FormMuttActiveTraditional):
    ACTION_CONTROLLER = ActionControllerSearch


class TestApp(npyscreen.NPSApp):
    def main(self):
        F = FmSearchActive()
        F.wStatus1.value = "Status Line "
        F.wStatus2.value = "Second Status Line "
        F.value.set_values([str(x) for x in range(500)])
        F.wMain.values = F.value.get()

        F.edit()


if __name__ == "__main__":
    App = TestApp()
    App.run() """

# !/usr/bin/env python
# encoding: utf-8
import sqlite3

import npyscreen

"""
import npyscreen, curses


class MyTestApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", MainForm())


class MainForm(npyscreen.FormWithMenus):
    def create(self):
        self.add(npyscreen.TitleText, name="Text:", value="Just some text.")
        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = self.exit_application

        # The menus are created here.
        self.m1 = self.add_menu(name="Main Menu", shortcut="^M")
        self.m1.addItemsFromList([
            ("Display Text", self.whenDisplayText, None, None, ("some text",)),
            ("Just Beep", self.whenJustBeep, "e"),
            ("Exit Application", self.exit_application, "é"),
        ])

        self.m2 = self.add_menu(name="Another Menu", shortcut="b", )
        self.m2.addItemsFromList([
            ("Just Beep", self.whenJustBeep),
        ])

        self.m3 = self.m2.addNewSubmenu("A sub menu", "^F")
        self.m3.addItemsFromList([
            ("Just Beep", self.whenJustBeep),
        ])

    def whenDisplayText(self, argument):
        npyscreen.notify_confirm(argument)

    def whenJustBeep(self):
        curses.beep()

    def exit_application(self):
        curses.beep()
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()


def main():
    TA = MyTestApp()
    TA.run()


if __name__ == '__main__':
    main()"""
class AddressDatabase(object):
    def __init__(self, filename="example-addressbook.db"):
        self.dbfilename = filename
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute(
        "CREATE TABLE IF NOT EXISTS records\
            ( record_internal_id INTEGER PRIMARY KEY, \
              last_name     TEXT, \
              other_names   TEXT, \
              email_address TEXT \
              )" \
            )
        db.commit()
        c.close()

    def add_record(self, last_name = '', other_names='', email_address=''):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('INSERT INTO records(last_name, other_names, email_address) \
                    VALUES(?,?,?)', (last_name, other_names, email_address))
        db.commit()
        c.close()

    def update_record(self, record_id, last_name = '', other_names='', email_address=''):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('UPDATE records set last_name=?, other_names=?, email_address=? \
                    WHERE record_internal_id=?', (last_name, other_names, email_address, \
                                                        record_id))
        db.commit()
        c.close()

    def delete_record(self, record_id):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('DELETE FROM records where record_internal_id=?', (record_id,))
        db.commit()
        c.close()

    def list_all_records(self, ):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT * from records')
        records = c.fetchall()
        c.close()
        return records

    def get_record(self, record_id):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT * from records WHERE record_internal_id=?', (record_id,))
        records = c.fetchall()
        c.close()
        return records[0]
class RecordList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(RecordList, self).__init__(*args, **keywords)
        self.add_handlers({
            "^A": self.when_add_record,
            "^D": self.when_delete_record
        })

    def display_value(self, vl):
        return "%s, %s" % (vl[1], vl[2])

    def actionHighlighted(self, act_on_this, keypress):
        self.parent.parentApp.getForm('EDITRECORDFM').value =act_on_this[0]
        self.parent.parentApp.switchForm('EDITRECORDFM')

    def when_add_record(self, *args, **keywords):
        self.parent.parentApp.getForm('EDITRECORDFM').value = None
        self.parent.parentApp.switchForm('EDITRECORDFM')

    def when_delete_record(self, *args, **keywords):
        self.parent.parentApp.myDatabase.delete_record(self.values[self.cursor_line][0])
        self.parent.update_list()

class RecordListDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = RecordList
    def beforeEditing(self):
        self.update_list()

    def update_list(self):
        self.wMain.values = self.parentApp.myDatabase.list_all_records()
        self.wMain.display()

class EditRecord(npyscreen.ActionForm):
    def create(self):
        self.value = None
        self.wgLastName   = self.add(npyscreen.TitleText, name = "Last Name:",)
        self.wgOtherNames = self.add(npyscreen.TitleText, name = "Other Names:")
        self.wgEmail      = self.add(npyscreen.TitleText, name = "Email:")

    def beforeEditing(self):
        if self.value:
            record = self.parentApp.myDatabase.get_record(self.value)
            self.name = "Record id : %s" % record[0]
            self.record_id          = record[0]
            self.wgLastName.value   = record[1]
            self.wgOtherNames.value = record[2]
            self.wgEmail.value      = record[3]
        else:
            self.name = "New Record"
            self.record_id          = ''
            self.wgLastName.value   = ''
            self.wgOtherNames.value = ''
            self.wgEmail.value      = ''

    def on_ok(self):
        if self.record_id: # We are editing an existing record
            self.parentApp.myDatabase.update_record(self.record_id,
                                            last_name=self.wgLastName.value,
                                            other_names = self.wgOtherNames.value,
                                            email_address = self.wgEmail.value,
                                            )
        else: # We are adding a new record.
            self.parentApp.myDatabase.add_record(last_name=self.wgLastName.value,
            other_names = self.wgOtherNames.value,
            email_address = self.wgEmail.value,
            )
        self.parentApp.switchFormPrevious()

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

class AddressBookApplication(npyscreen.NPSAppManaged):
    def onStart(self):
        self.myDatabase = AddressDatabase()
        self.addForm("MAIN", RecordListDisplay)
        self.addForm("EDITRECORDFM", EditRecord)

if __name__ == '__main__':
    myApp = AddressBookApplication()
    myApp.run()