import streamlit as st
from streamlit.web import utils
from urllib.parse import quote

# Add this near the top of your script, after imports
utils.add_route("/callback", lambda: None, method="GET")

def get_spotify_auth():
    encoded_redirect_uri = quote(REDIRECT_URI)
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=encoded_redirect_uri,
        scope='user-top-read',
        show_dialog=True
    )

def main():
    st.write(f"Debug - REDIRECT_URI: {REDIRECT_URI}")
    # Rest of your main function...
