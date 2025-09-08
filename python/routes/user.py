from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId
from database import db

router = APIRouter(prefix="/users", tags=["Users"])

def user_serializer(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"]
    }

@router.get("/")
async def list_users():
    users = []
    async for user in db["users"].find():
        users.append(user_serializer(user))
    return users

@router.get("/{user_id}")
async def get_user(user_id: str):
    try:
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    if user:
        return user_serializer(user)
    raise HTTPException(status_code=404, detail="User not found")
