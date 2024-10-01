import streamlit as st
import base64
import requests
import pandas as pd
from urllib.parse import quote
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import traceback

# Set up Streamlit page configuration
st.set_page_config(page_title='Spotify Top Tracks Analysis', page_icon=':musical_note:')

# Retrieve Spotify API credentials
def get_env_variable(var_name):
    try:
        value = st.secrets[var_name]
        return value
    except KeyError:
        st.error(f"Missing secret: {var_name}")
        return None

CLIENT_ID = get_env_variable("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = get_env_variable("SPOTIFY_CLIENT_SECRET")

# Initialize Spotify client
def get_spotify_client():
    st.write("Initializing Spotify client...")
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_top_tracks(sp):
    st.write("Fetching top tracks...")
    try:
        # Instead of user's top tracks, let's fetch a popular playlist
        playlist_id = '37i9dQZEVXbMDoHDwVN2tF'  # Global Top 50 playlist
        results = sp.playlist_tracks(playlist_id, limit=50)
        return results['items']
    except Exception as e:
        st.error(f"Error fetching tracks: {str(e)}")
        st.write(traceback.format_exc())
        return None
            
# Main app logic
def main():
    st.title('Spotify Top Tracks Analysis')
    st.write('Discover insights about top Spotify tracks.')

    try:
        st.write("Attempting to retrieve Spotify data...")
        sp = get_spotify_client()
        
        tracks = get_top_tracks(sp)
        
        if not tracks:
            st.warning("No tracks found. Please try again later.")
            return

        st.write(f"Found {len(tracks)} tracks.")
        
        st.write("Fetching audio features...")
        track_ids = [track['track']['id'] for track in tracks]
        audio_features = sp.audio_features(track_ids)
        
        if not audio_features:
            st.error("Failed to retrieve audio features. Please try again later.")
            return

        st.write("Creating DataFrame...")
        df = pd.DataFrame(audio_features)
        df['track_name'] = [track['track']['name'] for track in tracks]
        df.set_index('track_name', inplace=True)
        
        st.subheader('Audio Features of Top Tracks')
        st.write(df)
        
        numerical_columns = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']
        
        st.subheader('Visual Comparison of Audio Features')
        st.bar_chart(df[numerical_columns], height=400)
        
        st.subheader('Correlation Heatmap of Audio Features')
        correlation_matrix = df[numerical_columns].corr()
        st.write(correlation_matrix)
        
    except Exception as e:
        st.error(f"An error occurred while processing Spotify data: {str(e)}")
        st.write("Error details:", e)
        st.write("Error type:", type(e).__name__)
        st.write(traceback.format_exc())
    
   def get_access_token(auth_code):
    token_url = "https://accounts.spotify.com/api/token"
    authorization = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {authorization}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception(f"Token request failed with status {response.status_code}: {response.text}")
    return response.json()

if __name__ == "__main__":
    main()
