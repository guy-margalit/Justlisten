"""
ariel gal
the object that as access to our data base
"""
import sqlite3


class SongsGenreDatabase:
    def __init__(self, path):
        """
        builder
        """
        self.path = path

    def add_genre_and_song(self, song_number, genre_number):
        conn = sqlite3.connect(self.path)  # connect us to the database
        cur = conn.cursor()  # give us an access to execute the database
        cur.execute("insert into genre_and_songs (song_number, genre_number) values (?,?)", [song_number, genre_number])
        conn.commit()
        conn.close()
