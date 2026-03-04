import uuid
from fastapi import APIRouter, HTTPException
from models import UserCreate, LoginRequest, TokenResponse
from database import load_data, save_data
from hashing_password import get_password_hash, verify_password
from JWT_handler import create_access_token

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register(user: UserCreate):
    data = load_data()

    for u in data["users"]:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())  # ✅ unique ID generate

    new_user = {
        "user_id": user_id,
        "name": user.name,
        "email": user.email,
        "hashed_password": get_password_hash(user.password),
        "text": "",
        "texts": []
    }

    data["users"].append(new_user)
    save_data(data)

    token = create_access_token({"sub": user.email})

    # ✅ token ke saath user_id aur name bhi return
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id,
        "name": user.name
    }


@router.post("/login", response_model=TokenResponse)
def login(user: LoginRequest):
    data = load_data()

    db_user = next((u for u in data["users"] if u["email"] == user.email), None)

    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})

    # ✅ login mein bhi user_id aur name return
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_user["user_id"],
        "name": db_user["name"]
    }