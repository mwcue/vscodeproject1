import streamlit as st
import base64
import requests

# Set up Streamlit page configuration
st.set_page_config(page_title='Spotify API Debug', page_icon=':bug:')

# Debug: Print all available secrets
st.write("Debug - Available secrets:", list(st.secrets.keys()))

# Retrieve Spotify API credentials from Streamlit secrets
def get_env_variable(var_name):
    try:
        value = st.secrets[var_name]
        st.write(f"Debug - Retrieved {var_name}: {value[:5]}...{value[-5:]}")  # Show first and last 5 characters
        return value
    except KeyError:
        st.error(f"Missing secret: {var_name}")
        return None

CLIENT_ID = get_env_variable("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = get_env_variable("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = get_env_variable("REDIRECT_URI")

# Check if all required variables are set
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    st.error("Missing required secrets. Please check your Streamlit secrets.")
    st.stop()

# Main function to run the Streamlit app
def main():
    st.title('Spotify API Debug')
    st.write('This page is for debugging Spotify API authentication issues.')

    # Generate the authorization URL manually
    auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=user-top-read"
    st.write(f"Debug - Generated auth URL: {auth_url}")
    st.write(f"Please [click here]({auth_url}) to initiate Spotify login.")

    # Check for the authorization code in the URL
    query_params = st.query_params
    if 'code' in query_params:
        auth_code = query_params['code']
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
