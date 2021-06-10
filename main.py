import requests
from bs4 import BeautifulSoup
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import pprint

select_date = input("Which year do yo want to travel to? Type the date in this format YYYY-MM-DD: ")
# TODO: add some code to pop-up if the input date is invalid
url = "https://www.billboard.com/charts/hot-100/" + select_date

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
elements = soup.find_all(name="span", class_="chart-element__information__song")
artist_elements = soup.find_all(name="span", class_="chart-element__information__artist")
# Use list comprehension to get the song text from the html <span> elements which store the song name.
hot_100_songs = [song_element.getText() for song_element in elements]
artists = [artist.getText() for artist in artist_elements]

# print(f"{hot_100_songs}, {len(hot_100_songs)}")
# print(f"{artists}, {len(artists)}")

### ------- Connect to Spotify --------- ###
# note: environment variables are set
client_id = os.environ["SPOTIPY_CLIENT_ID"]
client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
redirect_uri = "http://example.com"

scope = "playlist-modify-private playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))
# results =
# results = sp.playlist_add_items()

### ------- Search an artist's top10 songs cover and preview ---------####
# radiohead_uri = 'spotify:artist:4Z8W4fKeB5YxbusRsdQVPb'
#
# spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
#
# results = spotify.artist_top_tracks(radiohead_uri)
#
# for track in results['tracks'][:10]:
#     print('track    : ' + track['name'])
#     print('audio    : ' + track['preview_url'])
#     print('cover art: ' + track['album']['images'][0]['url'])
#     print()

# ----------------SEARCH the song list in spotify api --------------------#

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

songs_uri_list = []
for index in range(0, 100):
    song_name = hot_100_songs[index]
    artist_name = artists[index]
    if "Featuring" in artist_name:
        artist_name = artist_name.replace("Featuring", "feat.")
        ### ---- TEST CODE HERE ----- ###
        # print(f"index={index}, {song_name}, artist:{artist_name}")
    results = spotify.search(q=f"{song_name} {artist_name}", type='track', limit=1)
    try:
        song_uri = results['tracks']['items'][0]['uri']
    except IndexError:
        # Catch errors if it cannot find any song in spotify
        ### ---- TEST CODE HERE ----- ###
        print(f"top:{index + 1} song: {hot_100_songs[index]}. No search result.")
        ### ---- CORRECTION ----- ###
        artist_name = artist_name.split()[0]
        results = spotify.search(q=f"{song_name} {artist_name}", type='track', limit=1)
        try:
            song_uri = results['tracks']['items'][0]['uri']
            print(f"search '{song_name} {artist_name}' instead")
        except IndexError:
            print(f"Still no search result. top{index + 1}, song: {song_name}, artist: {artist_name}")
        else:
            songs_uri_list.append(song_uri)
    else:
        # Only list the song uri if it finds a song, otherwise skip.
        songs_uri_list.append(song_uri)


# print(songs_uri_list)

# TODO: Figure out how to add year to the search

# TEST: search the song_name & artist to find the right song
# song_name = "Breaking Me"
# artist = 'Topic & A7S'
# results = spotify.search(q=f"{song_name} {artist}", type='track', limit=1)
# if not results['tracks']['items']:
#     print("no result")
#
# print(results)

### --- Create a new playlist and add songs in --- ###
user = "sb2828sb"
# user_profile = sp.user(user)
name = select_date + " Billboard 100"
create_new_playlist = sp.user_playlist_create(user, name, public=False, collaborative=False,
                                              description=f'Top 100 Billboard songs list in the week of selected date: '
                                                          f'{select_date}')
playlist_id = create_new_playlist['id']
sp.playlist_add_items(playlist_id=playlist_id, items=songs_uri_list)

print("Good job! Enjoy your music. :)")
