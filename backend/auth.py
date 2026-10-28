import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User

SECRET_KEY=os.getenv("SECRET_KEY","development-only-change-me")
ALGORITHM="HS256"
EXPIRE=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","120"))
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer=HTTPBearer(auto_error=False)

def hash_password(password): return pwd_context.hash(password)
def verify_password(password,password_hash): return pwd_context.verify(password,password_hash)
def create_access_token(user):
    exp=datetime.now(timezone.utc)+timedelta(minutes=EXPIRE)
    return jwt.encode({"sub":str(user.id),"username":user.username,"role":user.role,"exp":exp},SECRET_KEY,algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials|None=Depends(bearer), db:Session=Depends(get_db)):
    err=HTTPException(status_code=401,detail="Требуется вход в систему")
    if not credentials: raise err
    try:
        payload=jwt.decode(credentials.credentials,SECRET_KEY,algorithms=[ALGORITHM])
        uid=int(payload.get("sub",""))
    except (JWTError,ValueError,TypeError): raise err
    user=db.query(User).filter(User.id==uid).first()
    if not user: raise err
    return user

def require_admin(user:User=Depends(get_current_user)):
    if user.role!="Admin": raise HTTPException(status_code=403,detail="Доступ только для администратора")
    return user
