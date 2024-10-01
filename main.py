import streamlit as st
import base64
import requests
import pandas as pd
from urllib.parse import quote
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set up Streamlit page configuration
st.set_page_config(page_title='Spotify Top Tracks Analysis', page_icon=':musical_note:')

# Retrieve Spotify API credentials
def get_env_variable(var_name):
    if var_name == "REDIRECT_URI":
        return "https://vscodeproject1mwc.streamlit.app/"
    try:
        value = st.secrets[var_name]
        return value
    except KeyError:
        st.error(f"Missing secret: {var_name}")
        return None

CLIENT_ID = get_env_variable("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = get_env_variable("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "https://vscodeproject1mwc.streamlit.app/"

# Initialize Spotify client
def get_spotify_client():
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope='user-top-read',
        show_dialog=True
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def get_top_tracks_with_retry(sp, limit=50, time_range='medium_term', max_retries=3):
    for attempt in range(max_retries):
        try:
            st.write(f"Attempt {attempt + 1} to fetch top tracks...")
            return sp.current_user_top_tracks(limit=limit, time_range=time_range)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:  # Too Many Requests
                st.warning(f"Rate limit hit. Waiting for {e.headers.get('Retry-After', 5)} seconds.")
                time.sleep(int(e.headers.get('Retry-After', 5)))
            else:
                st.error(f"Spotify API error: {str(e)}")
                raise
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(5)
            
def main():
    st.title('Spotify Top Tracks Analysis App')
    st.write('Discover insights about your top Spotify tracks, yay!')

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
