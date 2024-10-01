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
    st.write('Discover insights about your top Spotify tracks.')

    # Initialize session state
    if 'auth_complete' not in st.session_state:
        st.session_state.auth_complete = False

    # Authentication flow
    if not st.session_state.auth_complete:
        auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={quote(REDIRECT_URI)}&scope=user-top-read"
        st.write(f"Please [click here]({auth_url}) to log in to Spotify.")
        
        query_params = st.experimental_get_query_params()
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            try:
                token_info = get_access_token(auth_code)
                st.session_state['access_token'] = token_info['access_token']
                st.session_state.auth_complete = True
                st.success("Successfully logged in to Spotify!")
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
    
    # Main app logic
    if st.session_state.auth_complete:
        try:
            st.write("Attempting to retrieve Spotify data...")
            sp = get_spotify_client()
            
            st.write("Fetching top tracks...")
            top_tracks = get_top_tracks_with_retry(sp)
            
            if not top_tracks or not top_tracks.get('items'):
                st.warning("No top tracks found. Try using Spotify more and check back later!")
                return

            st.write(f"Found {len(top_tracks['items'])} top tracks.")
            
            st.write("Fetching audio features...")
            track_ids = [track['id'] for track in top_tracks['items']]
            audio_features = sp.audio_features(track_ids)
            
            if not audio_features:
                st.error("Failed to retrieve audio features. Please try again later.")
                return

            st.write("Creating DataFrame...")
            df = pd.DataFrame(audio_features)
            df['track_name'] = [track['name'] for track in top_tracks['items']]
            df.set_index('track_name', inplace=True)
            
            st.subheader('Audio Features of Your Top Tracks')
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
            st.session_state.auth_complete = False
            if 'access_token' in st.session_state:
                del st.session_state['access_token']

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
