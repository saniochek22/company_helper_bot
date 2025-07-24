from pydantic import BaseModel

class UserBase(BaseModel):
    telegram_id: int
    username: str  
    role: str
    department: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    role: str | None = None
    department: str | None = None
    username: str | None = None  

class UserOut(BaseModel):
    telegram_id: int
    username: str
    role: str | None = None
    department: str | None = None

class BotTokenInput(BaseModel):
    token: str

class DepartmentCreate(BaseModel):
    name: str
    description_for_ai: str | None = None

class DepartmentOut(BaseModel):
    id: int
    name: str
    description_for_ai: str | None = None
