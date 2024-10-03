from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from minio_client import minio_client
from models import Asset, Private_Invitation, Transaction, User
from sqlalchemy.orm import Session

router = APIRouter()


# Internal function: Create public and private data rooms when an asset is listed for sale
def create_datarooms(asset_id: str):
    public_bucket_name = f"public-{asset_id}"
    private_bucket_name = f"private-{asset_id}"

    # Create public bucket if it doesn't exist
    if not minio_client.bucket_exists(public_bucket_name):
        minio_client.make_bucket(public_bucket_name)

    # Create private bucket if it doesn't exist
    if not minio_client.bucket_exists(private_bucket_name):
        minio_client.make_bucket(private_bucket_name)


# Internal function: Check access to the private data room
def check_private_access(asset_id: str, current_user: User, db: Session):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if current_user.id == asset.user_id and asset.status == "for_sale":
        raise HTTPException(
            status_code=403, detail="You do not have access to the private data room"
        )

    transaction = (
        db.query(Transaction)
        .filter_by(asset_id=asset_id, buyer_id=current_user.id)
        .first()
    )
    if transaction:
        return True  # Buyer has permanent access

    invitation = (
        db.query(Private_Invitation)
        .filter_by(asset_id=asset_id, invited_user_id=current_user.id)
        .first()
    )
    if not invitation:
        raise HTTPException(
            status_code=403, detail="You do not have access to this private data room"
        )

    return True


# Endpoint: List all files in the public data room
@router.get("/assets/{asset_id}/public/list-files")
def list_public_files(asset_id: str):
    public_bucket_name = f"public-{asset_id}"

    # Check if the public bucket exists
    if not minio_client.bucket_exists(public_bucket_name):
        raise HTTPException(
            status_code=404, detail="Public data room not found for this asset"
        )

    # List all files in the public bucket
    try:
        file_list = []
        objects = minio_client.list_objects(public_bucket_name)
        for obj in objects:
            file_list.append(obj.object_name)

        return {"files": file_list}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing public files: {str(e)}"
        )


# Endpoint: List all files in the private data room
@router.get("/assets/{asset_id}/private/list-files")
def list_private_files(
    asset_id: str,
    current_user: User = Depends(get_db),
    db: Session = Depends(get_db),
):
    private_bucket_name = f"private-{asset_id}"

    # Check access to the private data room
    check_private_access(asset_id, current_user, db)

    # Check if the private bucket exists
    if not minio_client.bucket_exists(private_bucket_name):
        raise HTTPException(
            status_code=404, detail="Private data room not found for this asset"
        )

    # List all files in the private bucket
    try:
        file_list = []
        objects = minio_client.list_objects(private_bucket_name)
        for obj in objects:
            file_list.append(obj.object_name)

        return {"files": file_list}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing private files: {str(e)}"
        )
