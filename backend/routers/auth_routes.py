from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, AuditLog
from schemas import UserCreate, UserOut, LoginRequest, Token
from auth import hash_password, verify_password, create_access_token, get_current_user
router=APIRouter(prefix="/auth",tags=["Авторизация"])
@router.post("/register",response_model=Token,status_code=201)
def register(data:UserCreate,db:Session=Depends(get_db)):
    if db.query(User).filter(or_(User.username==data.username,User.email==str(data.email))).first(): raise HTTPException(status_code=409,detail="Логин или email уже используются")
    user=User(username=data.username,email=str(data.email),password_hash=hash_password(data.password),role="Client");db.add(user);db.flush()
    db.add(AuditLog(actor_id=user.id,actor_username=user.username,action="register",entity="User",entity_id=user.id,details="Создан аккаунт клиента"));db.commit();db.refresh(user)
    return Token(access_token=create_access_token(user),user=user)
@router.post("/login",response_model=Token)
def login(data:LoginRequest,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==data.username).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(status_code=401,detail="Неверный логин или пароль")
    db.add(AuditLog(actor_id=user.id,actor_username=user.username,action="login",entity="User",entity_id=user.id,details="Успешный вход"));db.commit()
    return Token(access_token=create_access_token(user),user=user)
@router.get("/me",response_model=UserOut)
def me(user:User=Depends(get_current_user)): return user
