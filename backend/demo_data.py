# demo_data.py

# Dummy data for assets
demo_assets = {
    "Testseller": [
        {
            "id": "1",
            "name": "Demo Asset 1",
            "description": "Description for Demo Asset 1",
            "for_sale": True,
            "owner_id": "Testseller",  # Assuming user_id is a string
        },
        {
            "id": "2",
            "name": "Demo Asset 2",
            "description": "Description for Demo Asset 2",
            "for_sale": False,
            "owner_id": "Testseller",
        },
    ],
    "Testbuyer": [
        {
            "id": "3",
            "name": "Demo Asset 3",
            "description": "Description for Demo Asset 3",
            "for_sale": True,
            "owner_id": "Testbuyer",
        },
        {
            "id": "4",
            "name": "Demo Asset 4",
            "description": "Description for Demo Asset 4",
            "for_sale": True,
            "owner_id": "Testbuyer",
        },
    ],
}
