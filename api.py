from fastapi import FastAPI
import db
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


class MessageIn(BaseModel):
    telegram_id: int
    username: str
    message: str
    reply: str

app = FastAPI(
    title="AI Bot API",
    description="REST API поверх базы данных Telegram-бота",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # пока разрешаем всех (для разработки)
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Bot API работает 🚀"}

@app.get("/users")
def users():
    return db.get_all_users()

@app.get("/users/{user_id}/messages")
def user_messages(user_id: int):
    return db.get_user_messages(user_id)

@app.get("/stats")
def stats():
    return db.get_stats()
@app.post("/messages")
def create_message(msg: MessageIn):
    user_id = db.get_or_create_user(msg.telegram_id, msg.username)
    db.save_message(user_id, msg.message, msg.reply)
    return {"status": "ok", "user_id": user_id}