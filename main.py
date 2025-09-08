from fastapi import FastAPI
from routes import user, conversation, message, auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # URL frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(conversation.router)
app.include_router(message.router)
app.include_router(auth.router)
