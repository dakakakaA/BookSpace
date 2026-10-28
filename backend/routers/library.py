from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from auth import get_current_user, require_admin
from models import User, Book, Category, Loan, AuditLog
from schemas import BookIn, BookUpdate, BookOut, CategoryIn, CategoryOut, LoanCreate, LoanOut
books_router=APIRouter(prefix="/books",tags=["Каталог книг"])
categories_router=APIRouter(prefix="/categories",tags=["Категории"])
loans_router=APIRouter(prefix="/loans",tags=["Выдача книг"])
admin_router=APIRouter(prefix="/admin",tags=["Администрирование"])

def audit(db,user,action,entity,eid,details): db.add(AuditLog(actor_id=user.id,actor_username=user.username,action=action,entity=entity,entity_id=eid,details=details))
def book_or_404(db,bid):
    b=db.query(Book).filter(Book.id==bid).first()
    if not b: raise HTTPException(status_code=404,detail="Книга не найдена")
    return b
@books_router.get("",response_model=list[BookOut])
def list_books(search:str|None=Query(default=None,max_length=160),category_id:int|None=None,available:bool=False,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    q=db.query(Book).filter(Book.is_active.is_(True))
    if search: q=q.filter(or_(Book.title.ilike(f"%{search}%"),Book.author.ilike(f"%{search}%"),Book.isbn.ilike(f"%{search}%")))
    if category_id: q=q.filter(Book.category_id==category_id)
    if available: q=q.filter(Book.available_copies>0)
    return q.order_by(Book.title).all()
@books_router.get("/{book_id}",response_model=BookOut)
def get_book(book_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    b=book_or_404(db,book_id)
    if not b.is_active and user.role!="Admin": raise HTTPException(status_code=404,detail="Книга не найдена")
    return b
@books_router.post("",response_model=BookOut,status_code=201)
def create_book(data:BookIn,db:Session=Depends(get_db),admin:User=Depends(require_admin)):
    if db.query(Book).filter(Book.isbn==data.isbn).first(): raise HTTPException(status_code=409,detail="ISBN уже существует")
    if not db.query(Category).filter(Category.id==data.category_id,Category.is_active.is_(True)).first(): raise HTTPException(status_code=422,detail="Категория не найдена или отключена")
    values=data.model_dump(); values["available_copies"]=data.total_copies if data.available_copies is None else data.available_copies
    if values["available_copies"]>values["total_copies"]: raise HTTPException(status_code=422,detail="Доступно экземпляров больше, чем всего в библиотеке")
    b=Book(**values);db.add(b);db.flush();audit(db,admin,"create","Book",b.id,f"Добавлена книга: {b.title}");db.commit();db.refresh(b);return b
@books_router.put("/{book_id}",response_model=BookOut)
def update_book(book_id:int,data:BookUpdate,db:Session=Depends(get_db),admin:User=Depends(require_admin)):
    b=book_or_404(db,book_id);vals=data.model_dump(exclude_unset=True)
    if "isbn" in vals and db.query(Book).filter(Book.isbn==vals["isbn"],Book.id!=book_id).first(): raise HTTPException(status_code=409,detail="ISBN уже существует")
    if "category_id" in vals and not db.query(Category).filter(Category.id==vals["category_id"]).first(): raise HTTPException(status_code=422,detail="Категория не найдена")
    if "total_copies" in vals and vals["total_copies"] < (b.total_copies-b.available_copies): raise HTTPException(status_code=422,detail="Нельзя уменьшить фонд ниже числа выданных экземпляров")
    for k,v in vals.items(): setattr(b,k,v)
    if "total_copies" in vals and "available_copies" not in vals: b.available_copies=max(0,b.total_copies-(db.query(Loan).filter(Loan.book_id==b.id,Loan.status=="active").count()))
    if b.available_copies>b.total_copies: raise HTTPException(status_code=422,detail="Доступно экземпляров больше, чем всего")
    audit(db,admin,"update","Book",b.id,f"Изменена книга: {b.title}");db.commit();db.refresh(b);return b
@books_router.delete("/{book_id}",status_code=204)
def delete_book(book_id:int,db:Session=Depends(get_db),admin:User=Depends(require_admin)):
    b=book_or_404(db,book_id)
    if db.query(Loan).filter(Loan.book_id==b.id,Loan.status=="active").count(): raise HTTPException(status_code=409,detail="Нельзя удалить книгу с активной выдачей")
    audit(db,admin,"delete","Book",b.id,f"Скрыта книга: {b.title}");b.is_active=False;db.commit()
@categories_router.get("",response_model=list[CategoryOut])
def list_categories(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    q=db.query(Category)
    if user.role!="Admin":q=q.filter(Category.is_active.is_(True))
    return q.order_by(Category.name).all()
@categories_router.post("",response_model=CategoryOut,status_code=201)
def create_category(data:CategoryIn,db:Session=Depends(get_db),admin:User=Depends(require_admin)):
    if db.query(Category).filter(Category.name.ilike(data.name)).first(): raise HTTPException(status_code=409,detail="Категория уже существует")
    c=Category(**data.model_dump());db.add(c);db.flush();audit(db,admin,"create","Category",c.id,f"Добавлена категория: {c.name}");db.commit();db.refresh(c);return c
@categories_router.put("/{category_id}",response_model=CategoryOut)
def update_category(category_id:int,data:CategoryIn,db:Session=Depends(get_db),admin:User=Depends(require_admin)):
    c=db.query(Category).filter(Category.id==category_id).first()
    if not c: raise HTTPException(status_code=404,detail="Категория не найдена")
    if db.query(Category).filter(Category.name.ilike(data.name),Category.id!=category_id).first(): raise HTTPException(status_code=409,detail="Категория уже существует")
    for k,v in data.model_dump().items():setattr(c,k,v)
    audit(db,admin,"update","Category",c.id,f"Изменена категория: {c.name}");db.commit();db.refresh(c);return c
@categories_router.delete("/{category_id}",status_code=204)
def delete_category(category_id:int,db:Session=Depends(get_db),admin:User=Depends(require_admin)):
    c=db.query(Category).filter(Category.id==category_id).first()
    if not c: raise HTTPException(status_code=404,detail="Категория не найдена")
    if db.query(Book).filter(Book.category_id==c.id).count(): c.is_active=False
    else: db.delete(c)
    audit(db,admin,"delete","Category",category_id,"Удалена или скрыта категория");db.commit()
@loans_router.get("",response_model=list[LoanOut])
def list_loans(status:str|None=None,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    q=db.query(Loan)
    if user.role!="Admin":q=q.filter(Loan.user_id==user.id)
    if status:q=q.filter(Loan.status==status)
    return q.order_by(Loan.borrowed_at.desc()).all()
@loans_router.post("",response_model=LoanOut,status_code=201)
def borrow_book(data:LoanCreate,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    b=book_or_404(db,data.book_id)
    if not b.is_active: raise HTTPException(status_code=404,detail="Книга не найдена")
    if b.available_copies<1: raise HTTPException(status_code=409,detail="Нет доступных экземпляров")
    if db.query(Loan).filter(Loan.user_id==user.id,Loan.status=="active").count()>=5: raise HTTPException(status_code=409,detail="Можно иметь не более 5 активных выдач")
    loan=Loan(user_id=user.id,book_id=b.id,due_date=date.today()+timedelta(days=data.days),status="active");b.available_copies-=1;db.add(loan);db.flush();audit(db,user,"borrow","Loan",loan.id,f"Выдана книга #{b.id}: {b.title}");db.commit();db.refresh(loan);return loan
@loans_router.post("/{loan_id}/return",response_model=LoanOut)
def return_book(loan_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    q=db.query(Loan).filter(Loan.id==loan_id)
    if user.role!="Admin":q=q.filter(Loan.user_id==user.id)
    loan=q.first()
    if not loan: raise HTTPException(status_code=404,detail="Выдача не найдена")
    if loan.status!="active": raise HTTPException(status_code=409,detail="Эта книга уже возвращена")
    loan.status="returned";loan.returned_at=datetime.utcnow();loan.book.available_copies+=1;audit(db,user,"return","Loan",loan.id,f"Возвращена книга #{loan.book_id}");db.commit();db.refresh(loan);return loan
@admin_router.get("/audit")
def list_audit(limit:int=Query(default=200,ge=1,le=500),db:Session=Depends(get_db),admin:User=Depends(require_admin)):
    return [{"id":x.id,"actor_username":x.actor_username,"action":x.action,"entity":x.entity,"entity_id":x.entity_id,"details":x.details,"created_at":x.created_at} for x in db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()]
@admin_router.get("/stats")
def stats(db:Session=Depends(get_db),admin:User=Depends(require_admin)):
    return {"books":db.query(Book).filter(Book.is_active.is_(True)).count(),"users":db.query(User).count(),"active_loans":db.query(Loan).filter(Loan.status=="active").count(),"overdue":db.query(Loan).filter(Loan.status=="active",Loan.due_date<date.today()).count()}
