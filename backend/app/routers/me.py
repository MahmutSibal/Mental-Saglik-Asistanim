from fastapi import APIRouter, Depends
from ..deps import get_current_user_id
from ..db.mongodb import users_collection

router = APIRouter()

@router.get("/me")
async def me(user_id: str = Depends(get_current_user_id)):
    user = await users_collection().find_one({"_id": {"$eq": __import__('bson').ObjectId(user_id)}})
    if not user:
        return {"id": user_id}
    return {"id": user_id, "email": user.get("email"), "name": user.get("name")}
