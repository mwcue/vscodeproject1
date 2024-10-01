import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Set up Streamlit page configuration
st.set_page_config(page_title='Spotify Top Tracks Analysis', page_icon=':musical_note:')

# Retrieve Spotify API credentials
def get_env_variable(var_name):
    try:
        return st.secrets[var_name]
    except KeyError:
        st.error(f"Missing secret: {var_name}")
        return None

CLIENT_ID = get_env_variable("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = get_env_variable("SPOTIFY_CLIENT_SECRET")

# Initialize Spotify client
def get_spotify_client():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# variable for top x tracks
top_track_limit = 50

def get_top_tracks(sp):
    playlist_id = '37i9dQZEVXbMDoHDwVN2tF'  # Global Top 50 playlist
    results = sp.playlist_tracks(playlist_id, limit=top_track_limit)
    return results['items']
            
# Main app logic
def main():
    st.title('Spotify Top', top_track_limit, 'Tracks Analysis')
    st.write('Discover insights about top Spotify tracks.')

    sp = get_spotify_client()
    tracks = get_top_tracks(sp)
    
    if not tracks:
        st.warning("No tracks found. Please try again later.")
        return

    track_ids = [track['track']['id'] for track in tracks]
    audio_features = sp.audio_features(track_ids)
    
    if not audio_features:
        st.error("Failed to retrieve audio features. Please try again later.")
        return

    df = pd.DataFrame(audio_features)
    df['track_name'] = [track['track']['name'] for track in tracks]
    df.set_index('track_name', inplace=True)
    
    st.subheader('Audio Features of Top Tracks')
    st.write(df)

    # all features (but dropped 'loudness' b/c messed up the graph more)
    numerical_columns = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']

    st.subheader('Visual Comparison of all Audio Features')
    st.bar_chart(df[numerical_columns], height=500)
    
    st.subheader('Correlation Heatmap of Audio Features (Lower Triangle)')
    correlation_matrix = df[numerical_columns].corr()

   # dropped some features
    fewer_numerical_columns = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness']

    st.subheader('Visual Comparison of (fewer) Audio Features')
    st.bar_chart(df[fewer_numerical_columns], height=600)

    #heat map correlation of all features
    st.subheader('Correlation Heatmap of Audio Features (Lower Triangle)')
    correlation_matrix = df[numerical_columns].corr()
    # Create a mask for the lower triangle
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    # Create the heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, mask=mask, annot=False, cmap='Reds', vmin=-1, vmax=1, square=True)
    plt.title('Correlation Heatmap (Lower Triangle, all features)')
    st.pyplot(plt)

if __name__ == "__main__":
    main()
