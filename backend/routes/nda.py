from datetime import datetime
from secrets import ALGORITHMS, API_AUDIENCE, AUTH0_DOMAIN  # Import Auth0 configuration

from database import get_db  # Import the database session management
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from models import NDA, Asset, User  # Import NDA, User, and Asset models
from sqlalchemy.orm import Session

from minio import Minio

# Initialize the API router
router = APIRouter()

# Initialize the MinIO client
minio_client = Minio(
    "minio:9000",
    access_key="MINIO_ACCESS_KEY",
    secret_key="MINIO_SECRET_KEY",
    secure=False,
)

# OAuth2 Authorization using Auth0
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{AUTH0_DOMAIN}/authorize",
    tokenUrl=f"https://{AUTH0_DOMAIN}/oauth/token",
    scopes={"openid": "OpenID Connect standard scope"},
)


# Function to verify JWT token and extract user
def verify_jwt(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            f"https://{AUTH0_DOMAIN}/.well-known/jwks.json",
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        return payload  # Return the token payload (e.g., user information)
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


# Endpoint: Request NDA
# This endpoint allows a buyer to request an NDA for a specific asset
@router.post("/assets/{asset_id}/nda/request")
def request_nda(
    asset_id: str,
    buyer_id: str,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    buyer = db.query(User).filter(User.id == buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    existing_ndas = db.query(NDA).filter(NDA.asset_id == asset_id).count()
    nda_number = existing_ndas + 1

    new_nda = NDA(
        asset_id=asset_id,
        buyer_id=buyer_id,
        nda_number=nda_number,
        status="requested",
        requested_at=datetime.utcnow(),
    )
    db.add(new_nda)
    db.commit()

    return {
        "message": f"NDA number {nda_number} for asset {asset_id} has been requested."
    }


# Endpoint: Upload NDA
# This endpoint allows a buyer to upload the signed NDA and stores it in the MinIO bucket
@router.post("/assets/{asset_id}/nda/upload")
def upload_nda(
    asset_id: str,
    buyer_id: str,
    nda_number: int,
    nda_file: UploadFile,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    nda = (
        db.query(NDA)
        .filter_by(asset_id=asset_id, buyer_id=buyer_id, nda_number=nda_number)
        .first()
    )
    if not nda:
        raise HTTPException(status_code=404, detail="NDA not found")

    bucket_name = f"nda-{asset_id}"
    file_path = f"nda-{asset_id}-{nda_number}.pdf"

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    minio_client.fput_object(bucket_name, file_path, nda_file.file)

    nda.signed_at = datetime.utcnow()
    nda.status = "signed"
    db.commit()

    return {"message": "NDA has been uploaded and marked as signed."}


# Endpoint: Confirm NDA
# This endpoint allows the asset owner to confirm the NDA submitted by the buyer
@router.post("/assets/{asset_id}/nda/confirm")
def confirm_nda(
    asset_id: str,
    buyer_id: str,
    nda_number: int,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    nda = (
        db.query(NDA)
        .filter_by(asset_id=asset_id, buyer_id=buyer_id, nda_number=nda_number)
        .first()
    )
    if not nda:
        raise HTTPException(status_code=404, detail="NDA not found")

    nda.owner_confirmed_at = datetime.utcnow()
    nda.status = "confirmed"
    db.commit()

    return {"message": "NDA has been confirmed."}


# Endpoint: View NDA
# This endpoint allows either the seller or the buyer to view the NDA
@router.get("/assets/{asset_id}/nda/view")
def view_nda(
    asset_id: str,
    buyer_id: str,
    nda_number: int,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_jwt),
):
    nda = (
        db.query(NDA)
        .filter_by(asset_id=asset_id, buyer_id=buyer_id, nda_number=nda_number)
        .first()
    )
    if not nda:
        raise HTTPException(status_code=404, detail="NDA not found")

    current_user_id = token.get(
        "sub"
    )  # Extract the user ID from JWT token (Auth0 provides it under 'sub')

    if current_user_id != nda.buyer_id and current_user_id != nda.asset.user_id:
        raise HTTPException(
            status_code=403, detail="You are not authorized to view this NDA"
        )

    bucket_name = f"nda-{asset_id}"
    file_path = f"nda-{asset_id}-{nda_number}.pdf"

    try:
        response = minio_client.get_object(bucket_name, file_path)
        return StreamingResponse(response, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving NDA: {str(e)}")
