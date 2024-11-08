from pydantic import BaseModel
from datetime import datetime
from app.models.base import BaseResponse


class AddUser(BaseModel):
    name: str
    password: str

class UpdateUser(BaseModel):
    name: str|None = None
    password: str|None = None

class User(BaseModel):
    id: int
    name: str
    createdAt: datetime

class UserResponse(BaseResponse):
    data: User

class ListUserResponse(BaseResponse):
    items: list[User]
    offset: int
    limit: int