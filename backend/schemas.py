from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; username: str; email: EmailStr; role: str
class Token(BaseModel):
    access_token: str; token_type: str = "bearer"; user: UserOut
class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50); password: str = Field(min_length=1, max_length=128)
class CategoryIn(BaseModel):
    name: str = Field(min_length=2, max_length=80); description: str = Field(default="", max_length=2000); is_active: bool = True
class CategoryOut(CategoryIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
class BookIn(BaseModel):
    title: str = Field(min_length=1, max_length=200); author: str = Field(min_length=2, max_length=160)
    isbn: str = Field(min_length=10, max_length=20); category_id: int = Field(gt=0)
    publication_year: int | None = Field(default=None, ge=0, le=2100)
    description: str = Field(default="", max_length=5000); cover_url: str = Field(default="", max_length=500)
    total_copies: int = Field(default=1, ge=0, le=10000); available_copies: int | None = Field(default=None, ge=0, le=10000); is_active: bool = True
class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200); author: str | None = Field(default=None, min_length=2, max_length=160)
    isbn: str | None = Field(default=None, min_length=10, max_length=20); category_id: int | None = Field(default=None, gt=0)
    publication_year: int | None = Field(default=None, ge=0, le=2100); description: str | None = Field(default=None, max_length=5000)
    cover_url: str | None = Field(default=None, max_length=500); total_copies: int | None = Field(default=None, ge=0, le=10000)
    available_copies: int | None = Field(default=None, ge=0, le=10000); is_active: bool | None = None
class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; title: str; author: str; isbn: str; category_id: int; publication_year: int | None
    description: str; cover_url: str; total_copies: int; available_copies: int; is_active: bool; created_at: datetime
class LoanCreate(BaseModel):
    book_id: int = Field(gt=0); days: int = Field(default=14, ge=1, le=60)
class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; user_id: int; book_id: int; borrowed_at: datetime; due_date: date; returned_at: datetime | None; status: str
