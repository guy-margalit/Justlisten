import os
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy
import uuid
from justlisten.Utils import Utils

from justlisten.database import UsersDatabase
from justlisten.UsersPercentage import UsersPercentage
from justlisten.songsDatabase import SongsDatabase
from justlisten.users_and_songsDatabase import users_and_songsDatabase


PORT_NUMBER = 8080  # the port that the server run on
SPOTIPY_CLIENT_ID = 'f97d1c5036a046979fd80b06095282da'  # application id
SPOTIPY_CLIENT_SECRET = 'd57ba80dfd244a43a5e8139f21b6038a'  # application secret
SPOTIPY_REDIRECT_URI = 'http://80.178.34.235:8080'  # application uri
SCOPE = 'user-library-read playlist-modify-private user-read-currently-playing user-read-private'  # the variable that say what i will do with the client
DATABASE_PATH = "justlisten/database.db"


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    return caches_folder + session.get('uuid')


@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE,
                                               cache_handler=cache_handler,
                                               show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template("index.html", auth_url=auth_url)

    # Step 4. Signed in, display data
    sp = spotipy.Spotify(auth_manager=auth_manager)
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
    return render_template("home.html", artist1=artists[0][0], artist1_uri=artists[0][1], artist2=artists[1][0],
                        artist2_uri=artists[1][1], artist3=artists[2][0], artist3_uri=artists[2][1])

@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()


app.run(host='0.0.0.0', port=8080, threaded=True)  # run the server