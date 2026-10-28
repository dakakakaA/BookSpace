from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import Base,engine,SessionLocal
from models import User,Category,Book
from auth import hash_password
from routers import auth_routes,library

def seed_database():
    Base.metadata.create_all(bind=engine);db:Session=SessionLocal()
    try:
        if not db.query(User).filter(User.username=="client").first():db.add(User(username="client",email="reader@bookspace.local",password_hash=hash_password("client123"),role="Client"))
        if not db.query(User).filter(User.username=="admin").first():db.add(User(username="admin",email="admin@bookspace.local",password_hash=hash_password("admin123"),role="Admin"))
        categories=[("Художественная литература","Романы, рассказы и классика"),("Научная литература","Научно-популярные и академические издания"),("IT и программирование","Разработка, алгоритмы и технологии"),("Саморазвитие","Навыки, привычки и личная эффективность"),("Фэнтези и фантастика","Воображаемые миры и будущее")]
        for name,desc in categories:
            c=db.query(Category).filter(Category.name==name).first()
            if not c:c=Category(name=name,description=desc,is_active=True);db.add(c);db.flush()
        db.flush()
        sample=[("Мастер и Маргарита","Михаил Булгаков","9785171491755","Художественная литература",1967,"Роман о Москве, любви, свободе и загадочном визите Воланда.",8), ("Преступление и наказание","Фёдор Достоевский","9785170907150","Художественная литература",1866,"Психологический роман о нравственном выборе и ответственности.",5),("Чистый код","Роберт Мартин","9780132350884","IT и программирование",2008,"Практики написания понятного и поддерживаемого кода.",4),("Алгоритмы. Построение и анализ","Томас Кормен","9780321573513","IT и программирование",2009,"Фундаментальный учебник по алгоритмам и анализу сложности.",3),("Краткая история времени","Стивен Хокинг","9780553380163","Научная литература",1988,"Популярное введение в космологию и устройство Вселенной.",6),("Атомные привычки","Джеймс Клир","9780735211292","Саморазвитие",2018,"Система небольших изменений для формирования устойчивых привычек.",7),("Хоббит","Джон Р. Р. Толкин","9780547928227","Фэнтези и фантастика",1937,"Путешествие Бильбо Бэггинса к Одинокой горе.",4)]
        for title,author,isbn,cat,year,desc,copies in sample:
            if not db.query(Book).filter(Book.isbn==isbn).first():
                c=db.query(Category).filter(Category.name==cat).first();db.add(Book(title=title,author=author,isbn=isbn,category_id=c.id,publication_year=year,description=desc,total_copies=copies,available_copies=copies,is_active=True))
        db.commit()
    finally:db.close()
@asynccontextmanager
async def lifespan(app:FastAPI):
    seed_database();yield
app=FastAPI(title="BookSpace API",version="1.0.0",description="Электронная библиотека с каталогом, выдачей книг, ролями и аудитом",lifespan=lifespan)
app.include_router(auth_routes.router,prefix="/api")
app.include_router(library.books_router,prefix="/api")
app.include_router(library.categories_router,prefix="/api")
app.include_router(library.loans_router,prefix="/api")
app.include_router(library.admin_router,prefix="/api")
@app.get("/api/health")
def health():return {"status":"ok","service":"BookSpace API"}
