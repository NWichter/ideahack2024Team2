from database import engine, get_db
from fastapi import FastAPI
from middleware import AuthMiddleware
from models.assets_models import Asset
from models.user_models import User
from routes import user
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(user.router)


# Create the database tables
@app.on_event("startup")
def startup_event():
    import models.assets_models
    import models.user_models  # Ensure the models are imported to create the tables

    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    # Add demo data
    create_demo_data()


def create_demo_data():
    db: Session = next(get_db())

    # Check if demo data already exists
    if db.query(User).count() == 0:
        # Create demo users
        demo_users = [
            User(
                username="user1",
                email="user1@example.com",
                hashed_password="hashedpassword1",
                is_active=True,
            ),
            User(
                username="user2",
                email="user2@example.com",
                hashed_password="hashedpassword2",
                is_active=True,
            ),
            User(
                username="admin",
                email="admin@example.com",
                hashed_password="hashedpasswordadmin",
                is_active=True,
            ),
        ]
        db.add_all(demo_users)
        db.commit()

    if db.query(Asset).count() == 0:
        # Create demo assets
        demo_assets = [
            Asset(
                name="Asset 1",
                description="Description for Asset 1",
                owner_id=demo_users[0].id,
            ),
            Asset(
                name="Asset 2",
                description="Description for Asset 2",
                owner_id=demo_users[0].id,
                for_sale=True,
                price=1000.00,
            ),
            Asset(
                name="Asset 3",
                description="Description for Asset 3",
                owner_id=demo_users[1].id,
            ),
        ]
        db.add_all(demo_assets)
        db.commit()

    # Check if demo assets already exist
    if db.query(Asset).count() == 0:
        # Create demo assets
        demo_assets = [
            Asset(
                name="Asset 1",
                description="Description for Asset 1",
                owner_id=demo_users[0].id,
            ),
            Asset(
                name="Asset 2",
                description="Description for Asset 2",
                owner_id=demo_users[0].id,
                for_sale=True,
                price=1000.00,
            ),
            Asset(
                name="Asset 3",
                description="Description for Asset 3",
                owner_id=demo_users[1].id,
            ),
            Asset(
                name="Asset 4",
                description="Description for Asset 4",
                owner_id=demo_users[1].id,
                for_sale=True,
                price=500.00,
                additional_info="Special discount available",
            ),
            Asset(
                name="Asset 5",
                description="Description for Asset 5",
                owner_id=demo_users[2].id,
                for_sale=False,
            ),
        ]
        db.add_all(demo_assets)
        db.commit()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
