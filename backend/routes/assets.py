from typing import List

# from sqlalchemy.orm import Session  # Uncomment when using a database
# from utils.auth import verify_jwt  # JWT verification function from utils/auth.py
from demo_data import demo_assets  # Import demo assets from demo_data.py
from fastapi import APIRouter, HTTPException
from models.assets_models import Asset, AssetUpdate

router = APIRouter()


# Endpoint: Get assets for the current user
@router.get("/assets/me", response_model=List[Asset])
def get_user_assets():  # Remove the token dependency for now
    # user_id = token.get("sub")  # Extract user ID from JWT token
    user_id = "Testseller"  # For demonstration purposes, hardcoded user

    # Use demo assets based on the user_id
    if user_id in demo_assets:
        return demo_assets[user_id]

    raise HTTPException(status_code=404, detail="User not found")


# Endpoint: Offer an asset for sale
@router.post("/assets/{asset_id}/offer")
def offer_asset_for_sale(
    asset_id: str,
    sale_info: AssetUpdate,
    # token: dict = Depends(verify_jwt),  # JWT dependency removed
):
    user_id = "Testseller"  # For demonstration purposes, hardcoded user

    # Find the asset in demo data
    asset = next((a for a in demo_assets[user_id] if a["id"] == asset_id), None)
    if not asset:
        raise HTTPException(
            status_code=404, detail="Asset not found or not owned by the user"
        )

    # Update asset for sale information
    asset["for_sale"] = True
    asset["price"] = sale_info.price
    asset["additional_info"] = sale_info.additional_info

    return {"message": "Asset offered for sale successfully"}


# Endpoint: Get details of a specific asset
@router.get("/assets/{asset_id}", response_model=Asset)
def get_asset_details(
    asset_id: str,  # token: dict = Depends(verify_jwt),  # JWT dependency removed
):
    user_id = "Testseller"  # For demonstration purposes, hardcoded user

    asset = next((a for a in demo_assets[user_id] if a["id"] == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


# Endpoint: Update asset information
@router.patch("/assets/{asset_id}")
def update_asset(
    asset_id: str,
    updated_data: AssetUpdate,
    # token: dict = Depends(verify_jwt),  # JWT dependency removed
):
    user_id = "Testseller"  # For demonstration purposes, hardcoded user

    # Retrieve the asset from demo data
    asset = next((a for a in demo_assets[user_id] if a["id"] == asset_id), None)
    if not asset:
        raise HTTPException(
            status_code=404, detail="Asset not found or not owned by the user"
        )

    # Update asset data if provided
    if updated_data.name:
        asset["name"] = updated_data.name
    if updated_data.description:
        asset["description"] = updated_data.description

    return {"message": "Asset information updated successfully"}
