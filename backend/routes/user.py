from typing import List

from database import get_db  # Database session management
from fastapi import APIRouter, Depends, HTTPException
from models.user_models import (  # Import the User model and Pydantic models
    User,
    UserCreate,
    UserUpdate,
)
from sqlalchemy.orm import Session
from utils.auth import (
    verify_jwt,  # Import the JWT verification function from utils/auth.py
)

router = APIRouter()


# Endpoint: Get current user information (requires authentication)
@router.get("/user/me")
def get_current_user_info(
    token: dict = Depends(verify_jwt), db: Session = Depends(get_db)
):
    user_id = token.get("sub")  # Extract the user ID from the JWT token

    # Retrieve user information from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


# Endpoint: Update user information (authenticated user)
@router.patch("/user/{user_id}/update")
def update_user_info(
    user_id: str,
    update_data: UserUpdate,
    token: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    # Ensure that the user is updating their own profile
    if user_id != token.get("sub"):
        raise HTTPException(
            status_code=403, detail="You are not authorized to update this profile"
        )

    # Retrieve user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user data if provided
    if update_data.username:
        user.username = update_data.username
    if update_data.email:
        user.email = update_data.email

    db.commit()  # Save changes to the database
    return {"message": "User information updated successfully"}


# Admin Endpoint: Get all users (admin only)
@router.get("/users", response_model=List[dict])
def get_all_users(token: dict = Depends(verify_jwt), db: Session = Depends(get_db)):
    # Check if the user is an admin (this logic depends on your implementation, adjust accordingly)
    if "admin" not in token.get("roles", []):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    users = db.query(User).all()
    return [
        {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
        }
        for user in users
    ]


# Admin Endpoint: Create a new user (admin only)
@router.post("/user/create")
def create_user(
    user_data: UserCreate,
    token: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    # Check if the user is an admin
    if "admin" not in token.get("roles", []):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    # Check if email is already registered
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    # Create a new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=user_data.password,  # Assume you hash the password before saving
        is_active=True,
    )
    db.add(new_user)
    db.commit()

    return {"message": f"User {user_data.username} created successfully"}


# Admin Endpoint: Deactivate user account (admin only)
@router.patch("/user/{user_id}/deactivate")
def deactivate_user(
    user_id: str, token: dict = Depends(verify_jwt), db: Session = Depends(get_db)
):
    # Check if the current user is an admin
    if "admin" not in token.get("roles", []):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    # Retrieve the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Deactivate the user account
    user.is_active = False
    db.commit()

    return {"message": f"User {user.username} has been deactivated successfully"}
