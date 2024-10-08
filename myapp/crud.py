from sqlalchemy.orm import Session
from .models import User
from .auth import get_password_hash
from datetime import datetime

def create_book(db: Session, title: str, author: str, published_date: str):
    db_book = Book(title=title, author=author, published_date=datetime.strptime(published_date, '%Y-%m-%d').date())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_books(db):
    from myapp.models import Book
    return db.query(Book).all()


def get_book(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()

def update_book(db: Session, book_id: int, title: str, author: str, published_date: str):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book:
        db_book.title = title
        db_book.author = author
        db_book.published_date = datetime.strptime(published_date, '%Y-%m-%d').date()
        db.commit()
        db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book:
        db.delete(db_book)
        db.commit()

def create_user(db: Session, username: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()