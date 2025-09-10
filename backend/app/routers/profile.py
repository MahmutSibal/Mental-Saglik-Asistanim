import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from bson import ObjectId

from ..deps import get_current_user_id
from ..db.mongodb import users_collection
from ..schemas.profile import ProfileUpdate, PasswordChange, AvatarUploadResponse
from ..core.security import verify_password, get_password_hash


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    user = await users_collection().find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user["_id"]),
        "email": user.get("email"),
        "name": user.get("name"),
        "avatar_url": user.get("avatar_url"),
    }


@router.patch("/profile")
async def update_profile(payload: ProfileUpdate, user_id: str = Depends(get_current_user_id)):
    updates = {}
    if payload.name is not None:
        updates["name"] = payload.name
    if payload.email is not None:
        # Ensure email is unique
        existing = await users_collection().find_one({"email": payload.email, "_id": {"$ne": ObjectId(user_id)}})
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        updates["email"] = payload.email
    if not updates:
        return {"updated": False}
    await users_collection().update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    return {"updated": True, **updates}


@router.post("/profile/password")
async def change_password(payload: PasswordChange, user_id: str = Depends(get_current_user_id)):
    user = await users_collection().find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(payload.current_password, user.get("password", "")):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    hashed = get_password_hash(payload.new_password)
    await users_collection().update_one({"_id": ObjectId(user_id)}, {"$set": {"password": hashed}})
    return {"changed": True}


@router.post("/profile/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id)):
    # Basic validation
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    ext = os.path.splitext(file.filename or '')[1] or '.png'
    filename = f"{user_id}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    # Save file
    content = await file.read()
    with open(path, 'wb') as f:
        f.write(content)
    public_url = f"/uploads/{filename}"
    await users_collection().update_one({"_id": ObjectId(user_id)}, {"$set": {"avatar_url": public_url}})
    return AvatarUploadResponse(avatar_url=public_url)
