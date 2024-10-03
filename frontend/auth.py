import os

import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")


# Function to initiate the login process via Auth0 using Resource Owner Password Grant
def login(email, password):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    headers = {"Content-Type": "application/json"}
    payload = {
        "grant_type": "password",
        "username": email,
        "password": password,
        "audience": AUTH0_AUDIENCE,
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
    }
    response = requests.post(token_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()  # Return the token data
    else:
        st.error("Login failed. Please check your credentials.")
        return None


# Function to log out the user by clearing the session state
def logout():
    if "access_token" in st.session_state:
        del st.session_state["access_token"]
        del st.session_state["username"]
    st.success("You have been logged out.")
    st.experimental_rerun()


# Function to get the user info from Auth0 using the access token
def get_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"https://{AUTH0_DOMAIN}/userinfo", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch user information.")
        return None


# Function to display the current login status and options to log out
def display_logout():
    st.sidebar.markdown(f"### Logged in as: {st.session_state.get('username', 'User')}")
    if st.sidebar.button("Logout"):
        logout()


# Function to display the login form
def display_login_form():
    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email", type="default")  # Changed to 'default'
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        token_data = login(email, password)
        if token_data:
            st.session_state["access_token"] = token_data["access_token"]
            st.session_state["username"] = (
                email  # You can change this to the user's actual name from token_data
            )
