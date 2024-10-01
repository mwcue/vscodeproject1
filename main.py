import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import quote

# Set up Streamlit page configuration
st.set_page_config(page_title='Spotify Song Analysis', page_icon=':musical_note:')

# Debug: Print all available secrets
st.write("Debug - Available secrets:", list(st.secrets.keys()))

# Retrieve Spotify API credentials from Streamlit secrets
def get_env_variable(var_name):
    try:
        value = st.secrets[var_name]
        st.write(f"Debug - Retrieved {var_name}")
        return value
    except KeyError:
        st.error(f"Missing secret: {var_name}")
        return None

CLIENT_ID = get_env_variable("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = get_env_variable("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = get_env_variable("REDIRECT_URI")

# Check if all required environment variables are set
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    st.error("Missing required secrets. Please check your Streamlit secrets.")
    st.stop()

# Initialize Spotify authentication
def get_spotify_auth():
    encoded_redirect_uri = quote(REDIRECT_URI)
    st.write(f"Debug - Original REDIRECT_URI: {REDIRECT_URI}")
    st.write(f"Debug - Encoded REDIRECT_URI: {encoded_redirect_uri}")
    st.write(f"Debug - CLIENT_ID: {CLIENT_ID[:5]}...") # Show first 5 characters
    st.write(f"Debug - CLIENT_SECRET: {CLIENT_SECRET[:5]}...") # Show first 5 characters
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=encoded_redirect_uri,
        scope='user-top-read',
        show_dialog=True
    )

# Main function to run the Streamlit app
def main():
    st.title('Analysis of Your Top Spotify Tracks')
    st.write('Discover insights about your Spotify listening habits.')

    # Check for authentication status
    if 'spotify_auth' not in st.session_state:
        st.session_state['spotify_auth'] = None

    # debug line
    st.write("Debug - spotify_auth status:", 'spotify_auth' in st.session_state)
    
    # Handle Spotify authentication callback
    query_params = st.query_params
    if 'code' in query_params:
        try:
            auth_manager = get_spotify_auth()
            auth_manager.get_access_token(query_params['code'])
            st.session_state['spotify_auth'] = auth_manager
            st.query_params.clear()
            st.success("Successfully authenticated with Spotify!")
            st.rerun()
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return

    # If not authenticated, provide login link
    if st.session_state['spotify_auth'] is None:
        auth_manager = get_spotify_auth()
        auth_url = auth_manager.get_authorize_url()
        st.write(f"Please [click here]({auth_url}) to login to Spotify.")
        st.write("After logging in, you'll be redirected back to this app.")
        return

    # Create Spotify client
    sp = spotipy.Spotify(auth_manager=st.session_state['spotify_auth'])

    # ... rest of your code ...


    # Select numerical columns for the bar chart, excluding 'duration_ms'
    numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if 'duration_ms' in numerical_columns:
        numerical_columns.remove('duration_ms')
        numerical_columns.remove('tempo')
        numerical_columns.remove('time_signature')
        numerical_columns.remove('key')
        numerical_columns.remove('loudness')
        numerical_columns.remove('valence')
        numerical_columns.remove('mode')
        # numerical_columns.remove('energy')
        # numerical_columns.remove('danceability')


    except Exception as e:
        st.error(f"An error occurred while processing Spotify data: {str(e)}")
        st.session_state['spotify_auth'] = None  # Reset auth on error

# debug line
st.write("Debug - Script reached end without errors")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
