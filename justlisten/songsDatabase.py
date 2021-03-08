import sqlite3
"""
ariel gal
the object that as access to our data base
"""


class SongsDatabase:
    def __init__(self, path):
        """
        builder
        """
        self.path = path

    def add_song(self, song_name):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        song_id = self.get_song_number(song_name)
        if song_id is None:
            cur.execute("insert into songs (song_name) values (?)", [song_name])
            conn.commit()
        conn.close()
        return self.get_song_number(song_name)

    def get_song_number(self, name):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        try:
            song_number = cur.execute("SELECT (song_number) FROM songs WHERE song_name = '%s'" % name)
            song_number = list(song_number)[0][0]
        except Exception:
            song_number = None
        conn.close()
        return song_number

    def get_song_name(self, number):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        try:
            song_name = cur.execute("SELECT (song_name) FROM songs WHERE song_number = '%s'" % number)
            song_name = list(song_name)[0][0]
        except Exception:
            song_name = None
        conn.close()
        return song_name