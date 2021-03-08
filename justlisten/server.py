"""
ariel gal
just listen connect server and add in to database
"""
from flask import Flask, render_template, request, make_response
import spotipy
from spotipy import oauth2

from justlisten.Utils import Utils

from justlisten.database import UsersDatabase
from justlisten.UsersPercentage import UsersPercentage
from justlisten.songsDatabase import SongsDatabase
from justlisten.users_and_songsDatabase import users_and_songsDatabase


PORT_NUMBER = 8080  # the port that the server run on
SPOTIPY_CLIENT_ID = 'f97d1c5036a046979fd80b06095282da'  # application id
SPOTIPY_CLIENT_SECRET = 'd57ba80dfd244a43a5e8139f21b6038a'  # application secret
SPOTIPY_REDIRECT_URI = 'http://80.178.34.235:8080'  # application uri
SCOPE = 'user-library-read playlist-modify-private user-read-currently-playing'  # the variable that say what i will do with the client
DATABASE_PATH = "database.db"

sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE, open_browser=False)  #a variable that get access to the token_info
app = Flask(__name__)  # the server object


@app.route('/')  # connect to the function index
def index():
    """
    a function that connect the client
    """
    code = request.args.get('code')  # get the client code to the token
    if code:
        # if he already connect and he have a token
        print("Found Spotify auth code in Request URL! Trying to get valid access token...")
        token_info = sp_oauth.get_access_token(code)  # get the token info from the code
        access_token = token_info['access_token']  # get the token info from the code
        print("access_token:", access_token)
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)  # creating an object of the user

        song_database = SongsDatabase(DATABASE_PATH)
        users_percentage = UsersPercentage(DATABASE_PATH)
        users_songs_database = users_and_songsDatabase(DATABASE_PATH)
        users_database = UsersDatabase(DATABASE_PATH)

        user_id = sp.current_user()['id']
        user_number = users_database.get_user_number(user_id)
        print(user_number)
        print(user_id)

        tracks = []
        if user_number is None:
            user_number = users_database.add_user(user_id)
            total = 0
            try:
                while total < 1050:
                    items = sp.current_user_saved_tracks(limit=50, offset=total)['items']
                    for item in items:
                        tracks.append(item['track']['id'])
                    total += 50
            except Exception as e:
                print(e)
            for track_id in tracks[500:550]:
                number = song_database.add_song(track_id)
                users_songs_database.add_user_and_song(user_number, number)
            percentages = Utils.get_percentage(sp, tracks[500:550])
            for genre, percentage in percentages.items():
                users_percentage.add_user_genre(user_number, genre, percentage)
        else:
            tracks = users_songs_database.get_user_songs(user_number)
            tracks = [song_database.get_song_name(number) for number in tracks]
        print("tracks", tracks)
        tracks_artists = [sp.track(track)['artists'][0]['id'] for track in tracks[:100]]
        recent_artists = [sp.artist(artist_id) for artist_id in Utils.most_frequent(tracks_artists, 3)]
        artists = [(artist['name'], artist["images"][0]['url']) for artist in recent_artists]
        response = make_response(
            render_template("home.html", artist1=artists[0][0], artist1_uri=artists[0][1], artist2=artists[1][0],
                            artist2_uri=artists[1][1], artist3=artists[2][0], artist3_uri=artists[2][1]))
        response.set_cookie("access_token", access_token)
        return response
    else:
        return render_template("index.html", auth_url=sp_oauth.get_authorize_url())  # if he doesn't sign so its open our website that the client can sign up


@app.route("/artist")
def artist():
    artist_name = request.args.get('name')
    access_token = request.cookies.get("access_token")
    sp = spotipy.Spotify(access_token)
    artist_id = sp.search("artist:" + artist_name, limit=1, type="artist")['artists']['items'][0]['id']
    tracks = sp.artist_top_tracks(artist_id)['tracks']
    tracks_ids = [track['id'] for track in tracks]
    Utils.create_playlist(sp, artist_name + " Top Tracks", tracks_ids)
    return ""


@app.route("/generate")
def generate():
    access_token = request.cookies.get("access_token")
    sp = spotipy.Spotify(access_token)

    song_database = SongsDatabase(DATABASE_PATH)
    users_percentage = UsersPercentage(DATABASE_PATH)
    users_songs_database = users_and_songsDatabase(DATABASE_PATH)
    users_database = UsersDatabase(DATABASE_PATH)

    user_number = users_database.get_user_number(sp.current_user()['id'])
    closest_user = Utils.find_closest(users_database, users_percentage, user_number)
    new_tracks = Utils.get_new_songs(users_songs_database, song_database, user_number, closest_user)
    print(new_tracks)
    Utils.create_playlist(sp, "Songs For You", new_tracks)
    return ""


app.run(host='0.0.0.0', port=PORT_NUMBER, threaded=True)  # run the server

