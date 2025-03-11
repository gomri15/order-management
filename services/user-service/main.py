import uuid

from fastapi import FastAPI
from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password: str
    name: str

app = FastAPI()

db = {}

@app.post("/users/register")
def register(user: User):
    db[user.id] = user
    print(db)
    return {"message": "User registered successfully"}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    return db[user_id]