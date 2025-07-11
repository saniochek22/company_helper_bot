from pydantic import BaseModel

class UserBase(BaseModel):
    telegram_id: int
    role: str
    department: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    role: str | None = None
    department: str | None = None

class UserOut(UserBase):
    pass
