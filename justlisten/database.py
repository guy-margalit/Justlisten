import sqlite3
"""
ariel gal
the object that as access to our data base
"""


class UsersDatabase:
    def __init__(self, path):
        """
        builder
        """
        self.path = path

    def get_all_user_numbers(self):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        users_number = [number[0] for number in list(cur.execute("SELECT (user_number) FROM users"))]
        conn.close()
        return users_number

    def add_user(self, user_id):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        user_number = self.get_user_number(user_id)
        if user_number is None:
            cur.execute("insert into users (user_id) values (?)", [user_id])
            conn.commit()
        conn.close()
        return self.get_user_number(user_id)

    def get_user_number(self, user_id):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        try:
            user_number = cur.execute("SELECT (user_number) FROM users WHERE user_id = '%s'" % user_id)
            user_number = list(user_number)[0][0]
        except Exception:
            user_number = None
        conn.close()
        return user_number
