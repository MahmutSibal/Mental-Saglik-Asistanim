from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..schemas.auth import UserCreate, UserOut, Token
from ..core.security import get_password_hash, verify_password, create_access_token
from ..db.mongodb import users_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    col = users_collection()
    existing = await col.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user.password)
    doc = {
        "email": user.email,
        "password": hashed,
        "name": user.name,
        "created_at": datetime.utcnow(),
    }
    result = await col.insert_one(doc)
    return {"id": str(result.inserted_id), "email": user.email, "name": user.name}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    col = users_collection()
    user = await col.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_access_token(str(user["_id"]))
    return {"access_token": token, "token_type": "bearer"}
