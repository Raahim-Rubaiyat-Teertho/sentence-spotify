import streamlit as st

st.title("Sentence")

title = st.text_input("Sentence", "")

import json
import random
from langchain_community.llms import HuggingFaceHub
from dotenv import find_dotenv, load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# Load environment variables from .env
load_dotenv(find_dotenv())

id = os.getenv('CLIENT_ID')
secret = os.getenv('CLIENT_SECRET')

# Spotify Authentication
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=id, client_secret=secret))


emotion = ""

# LangChain LLM Prompt to detect emotion
prompt = f"""
    You will now work as an emotion analyzer. You will predict how a person is feeling based on the sentence they provide you with.
    THE SENTENCE:
    {title}

Output format:
    - Do not add any follow-up texts. Just one emotion response, do not provide possible emotions either. Just one. Just the format in JSON provided below:
    {{'emotion' : response}}
*
"""

# Use Hugging Face model as the LLM
llm = HuggingFaceHub(repo_id="deepseek-ai/DeepSeek-V3")

# Run a simple query
response = llm(prompt)
if '*' in response:
    response = response.split('*', 1)[1].strip()  # Get the text after '*'

# Ensure the response is a properly formatted JSON string
try:
    response_json = json.loads(response.replace("'", '"'))  # Convert single quotes to double quotes for valid JSON
    if(response_json['emotion'] == "anger"):
        emotion = 'angry'
    elif(response_json['emotion'] == "frustrated"):
        emotion = 'sad'

    elif(response_json['emotion'] == "sadness"):
        emotion = 'sad'

    elif(response_json['emotion'] == "excitement"):
        emotion = 'excited'
    else:
        emotion = response_json['emotion']
except json.JSONDecodeError:
    # print("Error: Response is not valid JSON", response)
    st.subheader("Something went wrong. Please try again")
    emotion = "Error"

print(f"Detected Emotion: {emotion}")
st.subheader(emotion)
# Search for Spotify playlists based on the detected emotion
search_query = f"{emotion} playlists"
playlists = sp.search(q=search_query, type='playlist', limit=5)


# Ensure there are playlists returned
if playlists and playlists.get('playlists') and playlists['playlists'].get('items'):
    # Get the playlist URIs
    playlist_uris = [playlist['uri'] for playlist in playlists['playlists']['items']]

    # Randomly select 5 playlists from the 10 playlists
    num_playlists = min(5, len(playlist_uris))  # Ensure we don’t sample more than available
    selected_playlists = random.sample(playlist_uris, num_playlists)  # Adjust sample size dynamically

    # print(f"Selected Playlists: {selected_playlists}")

    # For each selected playlist, randomly choose 1 song from it
    suggested_songs = []
    for playlist_uri in selected_playlists:
        tracks = sp.playlist_tracks(playlist_uri, limit=20)  # Fetch up to 20 tracks from each playlist
        if tracks and tracks.get('items'):
            random_track = random.choice(tracks['items'])  # Choose 1 random track from the playlist
            song_name = random_track['track']['name']
            song_url = random_track['track']['external_urls']['spotify']
            artist_names = ', '.join([artist['name'] for artist in random_track['track']['artists']])
            suggested_songs.append({'song_name': song_name, 'song_url': song_url, 'song_artist': artist_names})
        else:
            print(f"No tracks found for playlist {playlist_uri}")

    # Print suggested songs
    print("\nSuggested Songs from the Playlists:")
    for song in suggested_songs:
        print(f"Song: {song['song_name']}, URL: {song['song_url']}")
        st.page_link(f"{song['song_url']}", label=f"{song['song_name']} - {song['song_artist']}", use_container_width=True)
else:
    st.subheader("No playlists found for the given emotion.")
