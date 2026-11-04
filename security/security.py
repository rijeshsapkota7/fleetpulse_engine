import jwt
import bcrypt

def hash_password(plain_pswd : str) -> str:
    raw_pswd = plain_pswd.encode("utf-8")
    salt = bcrypt.gensalt()
    new_hashed_pass = bcrypt.hashpw(raw_pswd, salt)
    return new_hashed_pass.decode("utf-8")

def check_password(plain_pswd : str, hashed_pswd : str) -> bool:
    return bcrypt.checkpw(plain_pswd.encode("utf-8"), hashed_pswd.encode("utf-8"))