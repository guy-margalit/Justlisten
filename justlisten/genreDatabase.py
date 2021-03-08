import sqlite3
"""
ariel gal
the object that as access to our data base
"""


class GenreDatabase:
    def __init__(self, path):
        """
        builder
        """
        self.path = path

    def add_genre(self, genre_name):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        song_id = self.get_genre_number(genre_name)
        if song_id is None:
            cur.execute("insert into genres (genre_name) values (?)", [genre_name])
            conn.commit()
        conn.close()
        return self.get_genre_number(genre_name)

    def get_genre_number(self, name):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        try:
            genre_number = cur.execute("SELECT (genre_number) FROM genres WHERE genre_name = '%s'" % name)
            genre_number = list(genre_number)[0][0]
        except Exception:
            genre_number = None
        conn.close()
        return genre_number
