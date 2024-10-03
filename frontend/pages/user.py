import requests
import streamlit as st
from auth import display_login_form, get_user_info  # Import login and logout functions

API_URL = "http://localhost:8000"  # Define the API URL as a fallback


# Function to update user information
def update_user_info(user_id, access_token, update_data):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.patch(
        f"{API_URL}/user/{user_id}/update", headers=headers, json=update_data
    )
    return response.status_code == 200


# Display navigation drawer on the user management page
def display_drawer():
    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        st.experimental_set_query_params(page="home")
        st.experimental_rerun()
    if st.sidebar.button("User Management"):
        st.experimental_set_query_params(page="user")
        st.experimental_rerun()


# Main user management page
def user_management_page():
    st.title("User Management")
    display_drawer()  # Display drawer with navigation options

    # Check if the user is logged in
    if "access_token" in st.session_state:
        # Get user info from backend
        user_info = get_user_info(st.session_state["access_token"])
        if user_info:
            st.write(f"Username: {user_info['username']}")
            st.write(f"Email: {user_info['email']}")
            st.write(
                f"Account Status: {'Active' if user_info['is_active'] else 'Inactive'}"
            )

            # Update own profile
            st.subheader("Update Profile Information")
            with st.form(key="update_profile_form"):
                new_username = st.text_input(
                    "New Username", value=user_info["username"]
                )
                new_email = st.text_input("New Email", value=user_info["email"])
                update_profile_button = st.form_submit_button("Update Profile")

                if update_profile_button:
                    update_data = {"username": new_username, "email": new_email}
                    success = update_user_info(
                        user_info["user_id"],
                        st.session_state["access_token"],
                        update_data,
                    )
                    if success:
                        st.success("Profile updated successfully!")
                    else:
                        st.error("Failed to update profile.")
    else:
        # Display login form
        st.error("You must be logged in to view this page.")
        display_login_form()


# Check query parameters
query_params = st.query_params  # Updated line
if query_params.get("page") == ["user"]:
    user_management_page()
else:
    st.error("You don't have access to this page.")
    display_login_form()
