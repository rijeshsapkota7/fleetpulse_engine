from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from enum import Enum
from database.database import get_db
from database.model import Users
from security.security import hash_password, check_password, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

class RolesTypes(str, Enum):
    rider = "rider"
    customer = "customer"
    dispatcher = "dispatcher"

class UserCreate(BaseModel):
    name: str
    email : EmailStr
    password : str
    role : RolesTypes

class UserLogin(BaseModel):
    email : str
    password : str

@router.post("/signup", status_code=201)
def create_user(data : UserCreate, db : Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == data.email).first()
    if user:
        raise HTTPException(status_code=401, detail=f"User with email {data.email} already exists")
    hashed_password = hash_password(data.password)
    new_user = Users(name = data.name, email = data.email, password = hashed_password, role=data.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"Message" : "User Created succesfully", "Details" : new_user}


@router.post("/login")
def login_user(data : UserLogin, db : Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="email or password is incorrect")
    if check_password(data.password, user.password) is False:
        raise HTTPException(status_code=401, detail="email or password is incorrect")
    access_token = create_access_token(user.id, user.email)
    return {"token" : access_token, "type" : "bearer"}