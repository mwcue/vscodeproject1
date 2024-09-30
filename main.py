import streamlit as st
from streamlit.web import utils
from urllib.parse import quote
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

#debug statement
st.write("Debug - Script started")

# Add this near the top of your script, after imports
utils.add_route("/callback", lambda: None, method="GET")

def get_env_variable(var_name):
    try:
        value = st.secrets[var_name]
        st.write(f"Debug - {var_name}: {value}")  # Always print the value
        return value
    except KeyError:
        st.error(f"Missing environment variable: {var_name}")
        raise ValueError(f"Missing environment variable: {var_name}")
        
# Check if all required environment variables are set
#if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
#    st.error("Missing environment variables. Please check your .env file.")
#    st.stop()

# Initialize Spotify authentication
def get_spotify_auth():
    encoded_redirect_uri = quote(REDIRECT_URI)
    st.write(f"Debug - Encoded REDIRECT_URI: {encoded_redirect_uri}")
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=encoded_redirect_uri,
        scope='user-top-read',
        show_dialog=True
    )

# Place this before your main() function
st.write("Debug - About to retrieve environment variables")
try:
    CLIENT_ID = get_env_variable("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = get_env_variable("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = get_env_variable("REDIRECT_URI")
    st.write("Debug - Environment variables retrieved successfully")
except ValueError as e:
    st.error(str(e))
    st.stop()

# Main function to run the Streamlit app
def main():
    # debug: print 3 items (remove in production)
    st.write("Debug - Beginning of main()")
    st.write(f"Debug - REDIRECT_URI: {REDIRECT_URI}")
    st.write("Debug - Available secrets:", list(st.secrets.keys()))
    
    st.title('Analysis of Your Top Spotify Tracks')
    st.write('Discover insights about your Spotify listening habits.')
        # Debug: Print all secrets (remove in production)
    st.write("Available secrets:", list(st.secrets.keys()))
    st.write(f"Debug - REDIRECT_URI: {REDIRECT_URI}")
    
    # Check for authentication status
    if 'spotify_auth' not in st.session_state:
        st.session_state['spotify_auth'] = None

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
        #debug write line (remove in production)
        st.write("Debug - About to call get_spotify_auth()")
        auth_manager = get_spotify_auth()  
        auth_url = auth_manager.get_authorize_url()
        st.write(f"Please [click here]({auth_url}) to login to Spotify.")
        st.write("After logging in, you'll be redirected back to this app.")
        return

    # Create Spotify client
    sp = spotipy.Spotify(auth_manager=st.session_state['spotify_auth'])

    try:
        # Fetch user's top tracks
        st.info("Fetching your top tracks...")
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='long_term')
        st.success(f"Successfully fetched {len(top_tracks['items'])} top tracks")

        # Get audio features for top tracks
        track_ids = [track['id'] for track in top_tracks['items']]
        audio_features = sp.audio_features(track_ids)

        # Create DataFrame with track names and audio features
        df = pd.DataFrame(audio_features)
        df['track_name'] = [track['name'] for track in top_tracks['items']]
        df.set_index('track_name', inplace=True)

        # Display the data
        st.subheader('Audio Features of Your Top Tracks')
        st.write(df)

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

        # Create and display bar chart
        st.subheader('Visual Comparison of Audio Features')
        st.bar_chart(df[numerical_columns], height=600)

        # Optional: Display a heatmap of correlations between features
        st.subheader('Correlation Heatmap of Audio Features')
        correlation_matrix = df[numerical_columns].corr()
        st.write(correlation_matrix)

    except Exception as e:
        st.error(f"An error occurred while processing Spotify data: {str(e)}")
        st.session_state['spotify_auth'] = None  # Reset auth on error

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
