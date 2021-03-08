import sqlite3
"""
ariel gal
the object that as access to our data base
"""


class UsersPercentage:
    def __init__(self, path):
        """
        builder
        """
        self.path = path

    def add_user_genre(self, user_number, genre, percentage):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        cur.execute("insert into users_percentage (user_number, genre, percentage) values (?, ?, ?)", [user_number, genre, percentage])
        conn.commit()
        conn.close()

    def get_percentages(self, user_number):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        percentages = list(cur.execute("select genre, percentage from users_percentage where user_number=?", [user_number]))
        conn.commit()
        conn.close()
        return percentages
