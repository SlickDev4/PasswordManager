import sqlite3
import bcrypt
from os.path import exists
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
import encryption_and_decryption as encryption
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

'''
     Below are all the lists used for storing Widget's ID's
'''

# Login Page Lists
login_page_labels_ids = []
login_page_text_inputs_ids = []
login_page_buttons_ids = []

# New Account Page Lists
new_account_page_labels_ids = []
new_account_page_text_inputs_ids = []
new_account_page_buttons_ids = []

# Main Page Lists
main_page_labels_ids = []
main_page_text_inputs_ids = []
main_page_buttons_ids = []

# List storing the User ID in order to show only their table from the database
user_id_var = []

# List storing the Data Labels and Buttons IDs and Text
data_labels_ids = []
data_labels_text = []
edit_delete_buttons_ids = []

# List storing the Scroll ID
scroll = []

# Generating a different key every time to prevent from hacking the hashed passwords
salt = bcrypt.gensalt()

'''
General Functions - most of them returning dynamic values to the Classes
'''


# Clears the Data Labels Lists with IDs
def clear_data_labels_text():
    for i in range(len(data_labels_ids)):
        data_labels_ids[i].text = ''


# Clears the Main Page Lists with Text Input IDs
def clear_main_page_text_inputs():
    for i in range(len(main_page_text_inputs_ids)):
        main_page_text_inputs_ids[i].text = ''


# Clears the New Account Lists with Text Input IDs
def clear_new_account_text_inputs():
    for i in range(len(new_account_page_text_inputs_ids)):
        new_account_page_text_inputs_ids[i].text = ''


# Clears the Login Lists with All Widget IDs
def clear_login_widgets():
    login_page_labels_ids.clear()
    login_page_text_inputs_ids.clear()
    login_page_buttons_ids.clear()


# Returns the number of Labels that need to be created according to the number of Records
def number_of_records():
    conn = sqlite3.connect('credentials_database.db')
    c = conn.cursor()
    c.execute(f'SELECT COUNT(*) from passwords{user_id_var[0]}')
    result = c.fetchone()
    conn.commit()
    conn.close()
    return result[0] * 3


# Returns the number of Buttons that need to be created according to the number of Labels
def number_of_buttons():
    if number_of_records() == 0:
        return 0
    return int((number_of_records() / 3) * 2)


# Logout Function that clears the Login Page Lists and Initiates them again
def logout():
    clear_login_widgets()
    user_id_var.clear()

    screens[0].create_labels()
    screens[0].create_text_inputs()
    screens[0].create_buttons()


# Returns the correct row of data according to the pressed button and fills the text inputs with the data
def edit_correct_data(number):
    inc = 0

    for _ in range(number):
        inc += 1.5
    return int(inc)


# Returns the correct row of data according to the pressed button and saves the data from the text inputs
def save_correct_data(number):
    for button in edit_delete_buttons_ids:
        if button.state == "down":
            button.text = "Edit"
        button.disabled = False
    return int(number / 2) + 1


# Returns the correct row of data according to the pressed button and deletes that row
def delete_correct_data(number):
    inc = 1

    if number == 1:
        return inc

    for _ in range(number):
        inc += 0.5
    return int(inc)


# Initiates the Main Page Widgets
def main_page_widgets_init():
    screens[2].create_labels()
    screens[2].create_text_inputs()
    screens[2].create_buttons()
    screens[2].create_scroll_view()


# Initiates the New Account Page Widgets
def create_an_account_page_widgets_init():
    screens[1].create_labels()
    screens[1].create_text_inputs()
    screens[1].create_buttons()

    clear_login_widgets()


# Creates a personal table within the Database when a User creates an account
def create_personal_table_in_database():
    conn = sqlite3.connect('credentials_database.db')
    c = conn.cursor()
    c.execute(f"""CREATE TABLE if not exists passwords{user_id_var[0]}
            ( page text, username text, password text) """)
    conn.commit()
    conn.close()


'''
     Template Widgets Classes from kivy build file
'''


class AccountLabel(Label):
    pass


class DataLabel(Label):
    pass


class EditDeleteButtons(Button):
    pass


'''
     Classes
'''


class LogInPage(Screen):
    def __init__(self, **kwargs):
        super(LogInPage, self).__init__(**kwargs)
        self.create_labels()
        self.create_text_inputs()
        self.create_buttons()

        if not exists("secret.key"):
            encryption.generate_key()

    def create_labels(self):
        if len(login_page_labels_ids) == 0:
            for _ in range(2):
                labels = AccountLabel()
                self.add_widget(labels)
                login_page_labels_ids.append(labels)

            y = 0.6
            for label in login_page_labels_ids:
                label.pos_hint = {"x": 0.23, "y": y}
                y -= 0.1

            username_label = login_page_labels_ids[0]
            password_label = login_page_labels_ids[1]

            username_label.text = "Username"
            password_label.text = "Password"

    def create_text_inputs(self):
        if len(login_page_text_inputs_ids) == 0:
            for _ in range(2):
                text_inputs = TextInput(size_hint=(0.4, 0.05), multiline=False, write_tab=False)
                self.add_widget(text_inputs)
                login_page_text_inputs_ids.append(text_inputs)

            y = 0.6
            for text_input in login_page_text_inputs_ids:
                text_input.pos_hint = {"x": 0.35, "y": y}
                y -= 0.1

    def create_buttons(self):
        if len(login_page_buttons_ids) == 0:
            for _ in range(2):
                buttons = Button(size_hint=(0.2, 0.05))
                self.add_widget(buttons)
                login_page_buttons_ids.append(buttons)

            x = 0.25
            for button in login_page_buttons_ids:
                button.pos_hint = {"x": x, "y": 0.4}
                x += 0.25

            login_button = login_page_buttons_ids[0]
            create_an_account_button = login_page_buttons_ids[1]

            login_button.text = 'Login'
            create_an_account_button.text = 'Create an account'

            login_button.bind(on_press=self.validate_login)
            create_an_account_button.bind(on_press=self.create_an_account_page_transition)

    def main_page_transition(self, user_id):
        self.manager.current = 'MainPage'
        self.manager.transition.direction = 'left'

        user_id_var.append(user_id)

        create_personal_table_in_database()
        main_page_widgets_init()

    def create_an_account_page_transition(self, *_):
        self.manager.current = 'NewAccountPage'
        self.manager.transition.direction = 'right'
        create_an_account_page_widgets_init()

    def validate_login(self, *_):
        username_input = login_page_text_inputs_ids[0]
        password_input = login_page_text_inputs_ids[1]

        username = username_input.text.encode('utf-8')
        password = password_input.text.encode('utf-8')

        conn = sqlite3.connect('credentials_database.db')
        c = conn.cursor()
        c.execute("SELECT *, oid FROM users")
        records = c.fetchall()

        for record in records:
            username_db = record[1]
            password_db = record[2]

            if bcrypt.checkpw(username, username_db) and bcrypt.checkpw(password, password_db):
                self.main_page_transition(record[-1])
                break
        else:
            print('failed login')

        conn.commit()
        conn.close()


class NewAccountPage(Screen):
    def create_labels(self):
        if len(new_account_page_labels_ids) == 0:
            for _ in range(4):
                new_labels = AccountLabel()
                self.add_widget(new_labels)
                new_account_page_labels_ids.append(new_labels)

            y = 0.7
            for label in new_account_page_labels_ids:
                if y == 0.4:
                    y -= 0.1
                label.pos_hint = {"x": 0.23, "y": y}
                y -= 0.1

            email_label = new_account_page_labels_ids[0]
            username_label = new_account_page_labels_ids[1]
            password_label = new_account_page_labels_ids[2]
            captcha_label = new_account_page_labels_ids[3]

            email_label.text = "Email"
            username_label.text = "Username"
            password_label.text = "Password"
            captcha_label.text = "Captcha"

    def create_text_inputs(self):
        if len(new_account_page_text_inputs_ids) == 0:
            for _ in range(4):
                text_inputs = TextInput(size_hint=(0.4, 0.05), multiline=False, write_tab=False)
                self.add_widget(text_inputs)
                new_account_page_text_inputs_ids.append(text_inputs)

            y = 0.7
            for text_input in new_account_page_text_inputs_ids:
                if y == 0.4:
                    y -= 0.1
                text_input.pos_hint = {"x": 0.35, "y": y}
                y -= 0.1

    def create_buttons(self):
        if len(new_account_page_buttons_ids) == 0:
            for _ in range(2):
                buttons = Button(size_hint=(0.2, 0.05))
                self.add_widget(buttons)
                new_account_page_buttons_ids.append(buttons)

            x = 0.25
            for button in new_account_page_buttons_ids:
                button.pos_hint = {"x": x, "y": 0.2}
                x += 0.25

            submit_button = new_account_page_buttons_ids[0]
            cancel_button = new_account_page_buttons_ids[1]

            submit_button.text = 'Submit'
            cancel_button.text = 'Cancel'

            submit_button.bind(on_press=self.create_an_account_button)
            cancel_button.bind(on_press=self.logout)

    def logout(self, *_):
        self.manager.current = 'LogInPage'
        self.manager.transition.direction = 'left'
        logout()

    def create_an_account_button(self, *_):
        email_input = new_account_page_text_inputs_ids[0]
        username_input = new_account_page_text_inputs_ids[1]
        password_input = new_account_page_text_inputs_ids[2]

        username = username_input.text.encode('utf-8')
        password = password_input.text.encode('utf-8')

        encrypted_email = encryption.encrypt_message(email_input.text)
        hashed_username = bcrypt.hashpw(username, salt)
        hashed_password = bcrypt.hashpw(password, salt)

        conn = sqlite3.connect('credentials_database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (:email, :username, :password)",
                  {'email': encrypted_email,
                   'username': hashed_username,
                   'password': hashed_password})
        conn.commit()
        conn.close()

        clear_new_account_text_inputs()
        self.logout()


class MainPage(Screen):
    def create_labels(self):
        if len(main_page_labels_ids) == 0:
            for _ in range(3):
                labels = AccountLabel(size_hint=(0.2, 0.05))
                self.add_widget(labels)
                main_page_labels_ids.append(labels)

            y = 0.9
            for label in main_page_labels_ids:
                label.pos_hint = {"x": 0.05, "y": y}
                y -= 0.1

            page_label = main_page_labels_ids[0]
            username_label = main_page_labels_ids[1]
            password_label = main_page_labels_ids[2]

            page_label.text = "App/WebPage Name"
            username_label.text = "Username/Email"
            password_label.text = "Password"

    def create_text_inputs(self):
        if len(main_page_text_inputs_ids) == 0:
            for _ in range(3):
                text_inputs = TextInput(size_hint=(0.4, 0.05), multiline=False, write_tab=False)
                self.add_widget(text_inputs)
                main_page_text_inputs_ids.append(text_inputs)

            y = 0.9
            for text_input in main_page_text_inputs_ids:
                text_input.pos_hint = {"x": 0.27, "y": y}
                y -= 0.1

    def create_buttons(self):
        if len(main_page_buttons_ids) == 0:
            for _ in range(2):
                buttons = Button()
                self.add_widget(buttons)
                main_page_buttons_ids.append(buttons)

            add_password = main_page_buttons_ids[0]
            logout_button = main_page_buttons_ids[1]

            add_password.size_hint = (0.27, 0.25)
            add_password.pos_hint = {"x": 0.7, "y": 0.7}
            add_password.font_size = 20
            add_password.text = "Add Password"

            logout_button.size_hint = (0.2, 0.05)
            logout_button.pos_hint = {"x": 0.4, "y": 0.02}
            logout_button.text = "Logout"

            add_password.bind(on_press=self.add_password)
            logout_button.bind(on_press=self.logout)

    def create_scroll_view(self):
        if len(scroll) == 0:
            main_scroll = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint=(1.02, None),
                                     pos_hint={"x": 0.05, "y": 0.1},
                                     size=(Window.width - 10 / 100 * Window.width,
                                           Window.height - 45 / 100 * Window.height))
            self.add_widget(main_scroll)
            scroll.append(main_scroll)

            main_grid = GridLayout(cols=2, spacing=40, size_hint_y=None, size_hint_x=0.9)
            main_scroll.add_widget(main_grid)
            main_grid.bind(minimum_height=main_grid.setter('height'))

            data_labels_grid = GridLayout(cols=3, spacing=5, size_hint_y=None, size_hint_x=0.8)
            main_grid.add_widget(data_labels_grid)
            data_labels_grid.bind(minimum_height=data_labels_grid.setter('height'))

            buttons_grid = GridLayout(cols=2, spacing=5, size_hint_y=None, size_hint_x=0.3)
            main_grid.add_widget(buttons_grid)
            buttons_grid.bind(minimum_height=buttons_grid.setter('height'))

            for _ in range(number_of_records()):
                labels = DataLabel()
                data_labels_grid.add_widget(labels)
                data_labels_ids.append(labels)

            for _ in range(number_of_buttons()):
                buttons = EditDeleteButtons()
                buttons_grid.add_widget(buttons)
                edit_delete_buttons_ids.append(buttons)

            for index, button in enumerate(edit_delete_buttons_ids):
                if index % 2 == 0:
                    button.text = "Edit"
                    button.bind(on_press=self.edit_or_save)
                else:
                    button.text = "Delete"
                    button.bind(on_press=self.delete_record)

        self.populate_labels_with_data_from_the_database()

    def edit_or_save(self, *_):
        for button in edit_delete_buttons_ids:
            if button.state == "down":
                if button.text == "Edit":
                    button.text = "Save"
                    self.edit_record()
                else:
                    self.save_record()

    def edit_record(self):
        for self.button in edit_delete_buttons_ids:
            if not self.button.text == "Save":
                self.button.disabled = True

            if self.button.state == "down":
                butt_index = edit_delete_buttons_ids.index(self.button)
                data_text = edit_correct_data(butt_index)

                while True:
                    try:
                        main_page_text_inputs_ids[0].text = data_labels_text[data_text]
                        main_page_text_inputs_ids[1].text = data_labels_text[data_text + 1]
                        main_page_text_inputs_ids[2].text = data_labels_text[data_text + 2]
                    except IndexError:
                        pass

                    break

    def save_record(self):
        for button in edit_delete_buttons_ids:
            if button.state == "down":
                butt_index = edit_delete_buttons_ids.index(button)
                save_correct_data(butt_index)

                page_input = main_page_text_inputs_ids[0]
                username_input = main_page_text_inputs_ids[1]
                password_input = main_page_text_inputs_ids[2]

                encrypted_page = encryption.encrypt_message(page_input.text)
                encrypted_username = encryption.encrypt_message(username_input.text)
                encrypted_password = encryption.encrypt_message(password_input.text)

                conn = sqlite3.connect('credentials_database.db')
                c = conn.cursor()
                c.execute(f"""UPDATE passwords{user_id_var[0]} SET
                                    page = :page,
                                    username = :username,
                                    password = :password
                                    WHERE oid={save_correct_data(butt_index)}""",

                          {'page': encrypted_page,
                           'username': encrypted_username,
                           'password': encrypted_password})

                conn.commit()
                conn.close()

        self.populate_labels_with_data_from_the_database()
        clear_main_page_text_inputs()

    def delete_record(self, *_):
        for button in edit_delete_buttons_ids:
            if button.state == "down":
                butt_index = edit_delete_buttons_ids.index(button)
                record = delete_correct_data(butt_index)

                conn = sqlite3.connect('credentials_database.db')
                c = conn.cursor()
                c.execute(f"DELETE FROM passwords{user_id_var[0]} where oid={record}")
                c.execute(f"SELECT * FROM passwords{user_id_var[0]}")
                records = c.fetchall()
                temporary_storage_for_data = []
                for record in records:
                    for element in record:
                        temporary_storage_for_data.append(element)

                c.execute(f"DELETE FROM passwords{user_id_var[0]}")

                x = 0
                y = 1
                z = 2
                for _ in range(len(temporary_storage_for_data)):
                    try:
                        c.execute(f"INSERT INTO passwords{user_id_var[0]} VALUES (:page, :username, :password)",
                                  {'page': temporary_storage_for_data[x],
                                   'username': temporary_storage_for_data[y],
                                   'password': temporary_storage_for_data[z]})

                        x += 3
                        y += 3
                        z += 3
                    except IndexError:
                        pass

                conn.commit()
                conn.close()

        self.refresh_labels_and_buttons()
        self.populate_labels_with_data_from_the_database()

    def add_password(self, *_):
        page_input = main_page_text_inputs_ids[0]
        username_input = main_page_text_inputs_ids[1]
        password_input = main_page_text_inputs_ids[2]

        encrypted_page = encryption.encrypt_message(page_input.text)
        encrypted_username = encryption.encrypt_message(username_input.text)
        encrypted_password = encryption.encrypt_message(password_input.text)

        conn = sqlite3.connect('credentials_database.db')
        c = conn.cursor()
        c.execute(f"INSERT INTO passwords{user_id_var[0]} VALUES (:page, :username, :password)",
                  {'page': encrypted_page,
                   'username': encrypted_username,
                   'password': encrypted_password})

        conn.commit()
        conn.close()

        self.refresh_labels_and_buttons()
        self.populate_labels_with_data_from_the_database()
        clear_main_page_text_inputs()

    def logout(self, *_):
        self.manager.current = 'LogInPage'
        self.manager.transition.direction = 'right'

        self.remove_labels_and_buttons()
        clear_main_page_text_inputs()
        logout()

    def populate_labels_with_data_from_the_database(self):
        clear_data_labels_text()
        conn = sqlite3.connect('credentials_database.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM passwords{user_id_var[0]}")
        records = c.fetchall()

        data_labels_text.clear()

        for self.record in records:
            for element in self.record:
                data_labels_text.append(encryption.decrypt_message(element))

        for i in range(number_of_records()):
            data_labels_ids[i].text = data_labels_text[i]

        conn.commit()
        conn.close()

    def remove_labels_and_buttons(self):

        for button in main_page_buttons_ids:
            self.remove_widget(button)

        for button in edit_delete_buttons_ids:
            self.remove_widget(button)

        for label in data_labels_ids:
            self.remove_widget(label)

        self.remove_widget(scroll[0])

        scroll.clear()
        main_page_buttons_ids.clear()
        edit_delete_buttons_ids.clear()
        data_labels_ids.clear()

    def refresh_labels_and_buttons(self):
        self.remove_labels_and_buttons()
        self.create_buttons()
        self.create_scroll_view()


class Manager(ScreenManager):
    pass


kv = Builder.load_file("build.kv")
sm = Manager()

screens = [LogInPage(name='LogInPage'), NewAccountPage(name='NewAccountPage'), MainPage(name='MainPage')]

for screen in screens:
    sm.add_widget(screen)


class PasswordManagerApp(App):

    def build(self):
        self.create_database()
        return sm

    @staticmethod
    def create_database():
        conn = sqlite3.connect('credentials_database.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE if not exists users( email text, username text, password text ) """)
        conn.commit()
        conn.close()


if __name__ == '__main__':
    PasswordManagerApp().run()
