import requests
import streamlit as st
from auth import display_login_form

API_URL = "http://localhost:8000"  # Define the API URL as a fallback


# Function to get user assets from the backend
def get_user_assets(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{API_URL}/assets/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch assets.")
        return []


# Function to offer an asset for sale
def offer_asset_for_sale(asset_id, access_token, sale_info):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"{API_URL}/assets/{asset_id}/offer", headers=headers, json=sale_info
    )
    return response.status_code == 200


# Function to get asset details
def get_asset_details(asset_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{API_URL}/assets/{asset_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch asset details.")
        return None


# Function to update asset information
def update_asset(asset_id, access_token, updated_data):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.patch(
        f"{API_URL}/assets/{asset_id}", headers=headers, json=updated_data
    )
    return response.status_code == 200


# Main function for the assets management page
def assets_management_page():
    st.title("Assets Management")

    # User switch
    user = st.radio("Select User", ("Testseller", "Testbuyer"))

    # Get access token from session state
    access_token = st.session_state.get("access_token")

    # Display login form regardless of authentication status
    display_login_form()

    # Get user assets from the backend based on selected user
    if access_token:
        assets = get_user_assets(access_token)
    else:
        assets = []  # If not logged in, set assets to an empty list

    if assets:
        for asset in assets:
            if user == "Testseller" or (user == "Testbuyer" and asset["for_sale"]):
                st.subheader(asset["name"])
                st.write(f"Description: {asset['description']}")
                st.write(
                    f"Current Status: {'For Sale' if asset['for_sale'] else 'Not for Sale'}"
                )

                # Button to offer the asset for sale
                if user == "Testseller" and st.button(
                    "Offer for Sale", key=asset["id"]
                ):
                    sale_info = {
                        "price": st.number_input("Enter sale price", min_value=0.0),
                        "additional_info": st.text_area("Additional Information"),
                    }
                    if st.button("Submit Sale Offer"):
                        if offer_asset_for_sale(asset["id"], access_token, sale_info):
                            st.success(
                                f"Asset {asset['name']} is now available for sale!"
                            )
                        else:
                            st.error("Failed to offer asset for sale.")

                # Button to view asset details
                if st.button("View Asset Details", key=f"view_{asset['id']}"):
                    asset_details = get_asset_details(asset["id"], access_token)
                    if asset_details:
                        st.write("Asset Details:")
                        st.write(asset_details)

                        # Option to edit asset information for seller
                        if user == "Testseller" and st.button("Edit Asset"):
                            updated_name = st.text_input(
                                "New Asset Name", value=asset_details["name"]
                            )
                            updated_description = st.text_area(
                                "New Description", value=asset_details["description"]
                            )
                            updated_data = {
                                "name": updated_name,
                                "description": updated_description,
                            }
                            if st.button("Update Asset"):
                                if update_asset(
                                    asset["id"], access_token, updated_data
                                ):
                                    st.success("Asset updated successfully!")
                                else:
                                    st.error("Failed to update asset.")
    else:
        st.write("No assets found.")


# Check if the script is being run as the main entry point
if __name__ == "__main__":
    assets_management_page()
