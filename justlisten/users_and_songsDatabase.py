import sqlite3
"""
ariel gal
the object that as access to our data base
"""


class users_and_songsDatabase:
    def __init__(self, path):
        """
        builder
        """
        self.path = path

    def add_user_and_song(self, user_number, song_number):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        cur.execute("insert into users_and_songs (user_number, song_number) values (?,?)", [user_number, song_number])
        conn.commit()
        conn.close()

    def get_user_songs(self, user_number):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        songs = [song[0] for song in list(cur.execute("select (song_number) from users_and_songs where user_number=?", [user_number]))]
        conn.commit()
        conn.close()
        return songs
