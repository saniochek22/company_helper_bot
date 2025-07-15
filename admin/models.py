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

class UserOut(UserBase):
    pass

class BotTokenInput(BaseModel):
    token: str

class DepartmentCreate(BaseModel):
    name: str

class DepartmentOut(BaseModel):
    id: int
    name: str
