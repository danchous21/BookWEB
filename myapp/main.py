from typing import Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import crud, models, schemas
from .auth import get_password_hash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

Base.metadata.create_all(bind=engine)

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username

@app.post("/books/", response_model=schemas.Book)
def create_book(title: str, author: str, published_date: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return crud.create_book(db, title, author, published_date)

@app.get("/books/", response_model=list[schemas.Book])
def read_books(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return crud.get_books(db)

@app.get("/books/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    book = crud.get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, title: str, author: str, published_date: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    book = crud.update_book(db, book_id, title, author, published_date)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.delete("/books/{book_id}", response_model=dict)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    crud.delete_book(db, book_id)
    return {"message": "Book deleted"}

@app.post("/register/")
def register(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, username, password)

@app.post("/token/")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
