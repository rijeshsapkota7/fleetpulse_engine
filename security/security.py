import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database.database import get_db
from database.model import Users

secrete_key = "your_secure_fallback_secret_key_here"
algorithm =  "HS256"
security_scheme = HTTPBearer()

def hash_password(plain_pswd : str) -> str:
    raw_pswd = plain_pswd.encode("utf-8")
    salt = bcrypt.gensalt()
    new_hashed_pass = bcrypt.hashpw(raw_pswd, salt)
    return new_hashed_pass.decode("utf-8")

def check_password(plain_pswd : str, hashed_pswd : str) -> bool:
    return bcrypt.checkpw(plain_pswd.encode("utf-8"), hashed_pswd.encode("utf-8"))

def create_access_token(user_id : int = None, user_email : str = None, exp : int = 30) -> str:
    future_time = datetime.now(timezone.utc) + timedelta(minutes=exp)
    exp_time = int(future_time.timestamp()) 
    payload = {
        "user_id" : user_id,
        "user_email" : user_email,
        "exp" : exp_time
    }
    access_token = jwt.encode(payload, secrete_key, algorithm)
    return access_token

def verify_token(credentials : HTTPAuthorizationCredentials = Depends(security_scheme) , db : Session = Depends(get_db)):
    token = credentials.credentials
    try:
        decode_token = jwt.decode(token, secrete_key, algorithms=[algorithm])
        user_id = decode_token.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="token in invalid or expired")
    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user

def verify_Ws_connection(token : str, db : Session = Depends(get_db)) -> Users:
    try:
        decode_token = jwt.decode(token, secrete_key, algorithms=[algorithm])
        user_id = decode_token.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="token in invalid or expired")
    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user
