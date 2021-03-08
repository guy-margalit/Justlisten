
from songsDatabase import SongsDatabase


def main():

    """
    Add Documentation here
    """
    songs = SongsDatabase(r"C:\Users\guyma\OneDrive\מסמכים\justlisten\database.db")
    songs.add_song("guys_song")
    print(songs.get_song_number("guys_song"))
    songs.close()


if __name__ == '__main__':
    main()
