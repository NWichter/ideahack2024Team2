import streamlit as st
from auth import display_login_form, display_logout, get_user_info

# Set page configuration
st.set_page_config(
    page_title="DealClub.",
    page_icon="🛒",  # Optional icon
)

# Title
st.title("DealClub.")

# Project description
st.header("Project Description")
st.write(
    """
Welcome to our innovative marketplace for a management tool specifically designed for family offices. 
Our goal is to create a platform that simplifies the trading of various illiquid assets and 
ensures a fair and transparent exchange between buyers and sellers.
"""
)

# Features section
st.header("Key Features")
st.write(
    """
- **Easy Asset Management**: Users can manage their assets and list them for sale.
- **Transparent Offers**: Buyers can make fair offers on assets.
- **Data Room**: A secure data room for buyers to access essential information about the assets, ensuring transparency and trust.
- **Secure Environment**: Privacy and data security are our top priorities.
"""
)

# Contact section
# st.header("Contact")
# st.write("For questions or suggestions, please contact us at: info@familyoffice.com")


# Function to handle the callback from Auth0 after successful authentication
def handle_auth_callback():
    query_params = st.query_params  # Updated line

    # Extract access token from URL fragment
    if "access_token" in query_params:
        st.session_state["access_token"] = query_params["access_token"][0]
        user_info = get_user_info(st.session_state["access_token"])
        if user_info:
            st.session_state["username"] = user_info["name"]


# Function to display the drawer with all possible pages
def display_drawer():
    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        st.experimental_set_query_params(page="home")
        st.experimental_rerun()
    if st.sidebar.button("User Management"):
        st.experimental_set_query_params(page="user")
        st.experimental_rerun()


# Main function to render the home page
def main_page():
    # Handle authentication callback from Auth0
    handle_auth_callback()

    # Check if user is logged in (access_token is in session)
    if "access_token" in st.session_state:
        display_logout()  # Show logout option if logged in
        display_drawer()  # Display drawer with navigation options
        st.write("You are logged in. Access additional features from the sidebar.")
    else:
        display_login_form()  # Show login form if not logged in


# Check if the script is being run as the main entry point
if __name__ == "__main__":
    main_page()
