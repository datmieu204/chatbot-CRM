from fastapi import APIRouter, HTTPException, status
from database import db
from model import User
from pydantic import BaseModel, EmailStr
import bcrypt
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "supersecret"   # 🔥 bạn nên để trong biến môi trường
ALGORITHM = "HS256"

# Schema cho login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Đăng ký ----------
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: User):
    # Check email tồn tại chưa
    if await db["users"].find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_data = user.model_dump(exclude={"id"})
    user_data["password"] = hashed_password

    # Insert user
    try:
        result = await db["users"].insert_one(user_data)
    except DuplicateKeyError:
        # tránh race condition
        raise HTTPException(status_code=400, detail="Email already registered")

    created = await db["users"].find_one({"_id": result.inserted_id}, {"password": 0})

    payload = {
        "user_id": str(result.inserted_id),           
        "email": created["email"],                    
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"id": str(created["_id"]), "email": created["email"], "access_token": token}


# ---------- Đăng nhập ----------
@router.post("/login")
async def login(request: LoginRequest):
    # Tìm user theo email
    user = await db["users"].find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Kiểm tra mật khẩu
    if not bcrypt.checkpw(request.password.encode("utf-8"), user["password"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Tạo JWT token
    payload = {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(hours=2)  # token hết hạn sau 2h
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "payload":payload, "token_type": "bearer"}
