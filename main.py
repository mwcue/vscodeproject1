import streamlit as st
import base64
import requests
from urllib.parse import quote

# Set up Streamlit page configuration
st.set_page_config(page_title='Spotify API Debug', page_icon=':bug:')

# Debug: Print all available secrets
st.write("Debug - Available secrets:", list(st.secrets.keys()))

# Retrieve Spotify API credentials from Streamlit secrets
def get_env_variable(var_name):
    if var_name == "REDIRECT_URI":
        return "https://vscodeproject1mwc.streamlit.app/"
    try:
        value = st.secrets[var_name]
        st.write(f"Debug - Retrieved {var_name}: {value}")
        return value
    except KeyError:
        st.error(f"Missing secret: {var_name}")
        return None

CLIENT_ID = get_env_variable("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = get_env_variable("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "https://vscodeproject1mwc.streamlit.app/"

st.write(f"Debug - Hardcoded REDIRECT_URI: {REDIRECT_URI}")

# Check if all required variables are set
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    st.error("Missing required secrets. Please check your Streamlit secrets.")
    st.stop()

# Main function to run the Streamlit app
def main():
    st.title('Spotify API Debug')
    st.write('This page is for debugging Spotify API authentication issues.')

    # Print full REDIRECT_URI for debugging
    st.write(f"Debug - Full REDIRECT_URI: {REDIRECT_URI}")

    # Generate the authorization URL manually
    encoded_redirect_uri = quote(REDIRECT_URI)
    auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={encoded_redirect_uri}&scope=user-top-read"
    st.write(f"Debug - Generated auth URL: {auth_url}")
    st.write(f"Please [click here]({auth_url}) to initiate Spotify login.")

    # Check for the authorization code in the URL
    query_params = st.experimental_get_query_params()
    st.write(f"Debug - Full query parameters: {query_params}")
    
    if 'error' in query_params:
        st.error(f"Authentication error: {query_params['error'][0]}")
        st.write(f"Debug - Full error description: {query_params.get('error_description', ['No description provided'])[0]}")
    elif 'code' in query_params:
        auth_code = query_params['code'][0]
        st.write(f"Debug - Received auth code: {auth_code[:5]}...{auth_code[-5:]}")

        # Exchange the authorization code for an access token
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
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            st.write(f"Debug - Token exchange response status: {response.status_code}")
            st.write(f"Debug - Token exchange response content: {response.text}")
            
            if response.status_code == 200:
                token_info = response.json()
                st.success("Successfully authenticated with Spotify!")
                st.write(f"Access Token: {token_info['access_token'][:10]}...")
            else:
                st.error(f"Failed to exchange auth code for token. Status: {response.status_code}")
        except Exception as e:
            st.error(f"An error occurred during token exchange: {str(e)}")
    else:
        st.write("Waiting for authorization code...")

if __name__ == "__main__":
    main()
