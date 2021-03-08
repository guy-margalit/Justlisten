

BASIC_GENRES = [
    'pop',
    'rap',
    'hip hop',
    'metal',
    'rock',
    'trap',
    'jazz',
    'blues',
    'dance',
    'soul',
    'country'
]


def get_general_genre(genre):
    for basic_genre in BASIC_GENRES:
        if basic_genre in genre:
            return basic_genre
    return genre


def match_genres(genre1, genre2):
    matched = 0
    genre1_words = genre1.split()
    genre1_length = len(genre1_words)
    genre2_words = genre2.split()
    for word in genre2_words:
        if word in genre1_words:
            matched += 1
            genre1_words.remove(word)
    print(genre1, genre2, matched / genre1_length)
    return matched / genre1_length


def song_distance(sp, song1_id, song2_id):
    if song1_id == song2_id:
        return 0
    song1 = sp.track(song1_id)
    song2 = sp.track(song2_id)
    if song1["album"] == song2["album"]:
        return 1
    match = 0
    song1_genres_count = 0
    song2_genres = []
    for artist2 in song2['artists']:
        genres = sp.artist(artist2['id'])['genres']
        song2_genres += genres
    print("song2_genres", song2_genres)
    for artist1 in song1['artists']:
        genres = sp.artist(artist1['id'])['genres']
        for genre in genres:
            matches = []
            for genre1 in song2_genres:
                genre_match = match_genres(genre, genre1)
                matches.append(genre_match)
            song1_genres_count += 1
            match += max(matches)
    return 3 - (match / song1_genres_count)


def get_percentage(sp, songs):
    total = 0
    genre_count = {}
    for song_id in songs:
        song = sp.track(song_id)
        for artist_id in song['artists']:
            artist = sp.artist(artist_id['id'])
            for genre in artist['genres']:
                total += 1
                genre = get_general_genre(genre)
                count = genre_count.get(genre)
                if count is not None:
                    genre_count.update({genre: count + 1})
                else:
                    genre_count.update({genre: 1})
    percentage = {}
    for genre, count in genre_count.items():
        percentage.update({genre: round(count / total * 100, 2)})
    return percentage


def most_frequent(lst, count):
    return sorted(set(lst), key=lst.count)[-count:][::-1]


def percentages_contains(percentages, genre):
    for genre1, percentage in percentages:
        if genre1 == genre:
            return percentage
    return None


def get_percentages_distance(percentages1, percentages2):
    distance = 0
    for genre, percentage in percentages1:
        if percentages_contains(percentages2, genre) is not None:
            distance += max([0, percentage - percentages_contains(percentages2, genre)])
        else:
            distance += percentage
    return distance


def find_closest(users_database, percentages_database, user_number):
    closest_number = 0
    closest_distance = 200
    my_percentages = percentages_database.get_percentages(user_number)
    users = users_database.get_all_user_numbers()
    for number in users:
        if number != user_number:
            percentages = percentages_database.get_percentages(number)
            distance = get_percentages_distance(my_percentages, percentages)
            if distance < closest_distance:
                closest_number = number
    return closest_number


def get_new_songs(users_songs_database, song_database, user_number, closest, limit=20):
    my_tracks = users_songs_database.get_user_songs(user_number)
    my_tracks = [song_database.get_song_name(number) for number in my_tracks]
    closest_tracks = users_songs_database.get_user_songs(closest)
    closest_tracks = [song_database.get_song_name(number) for number in closest_tracks]
    different_tracks = list(filter(lambda x: x not in my_tracks, closest_tracks))
    return different_tracks[:limit]


def create_playlist(sp, name, tracks):
    sp.user_playlist_create(sp.current_user()['id'], name, public=False,
                            description="Created by JustListen")
    sp.playlist_add_items(
        sp.search("playlist:" + name, limit=1, type="playlist")["playlists"]['items'][0]['id'],
        tracks)
