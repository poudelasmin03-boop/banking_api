from pydoc import plain
from warnings import deprecated
from typing import Optional
import bcrypt
from fastapi import FastAPI, APIRouter, Form, Depends, HTTPException, status

from passlib.ifc import PasswordHash
from sqlalchemy import Column
from jose import JWTError, jwt

from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database.db import engine, Base, get_db

from bankingAPi.models.bank import DbUser

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm.session import Session


router = APIRouter(prefix="/user", tags=["user"])

pwdContext = CryptContext(schemes=["argon2"], deprecated="auto")

oAuth2 = OAuth2PasswordBearer(tokenUrl="/user/login")


class Hash:
    def Hash_password(password: str):
        return pwdContext.hash(password)

    def verify(hashed_password: str, plain_password: str):
        return pwdContext.verify(plain_password, hashed_password)


@router.post("/register")
def register_user(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    existing_email = db.query(DbUser).filter(DbUser.email == email).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist."
        )

    user = DbUser(username=username, password=Hash.Hash_password(password), email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "message": f"{username} Successfully register",
    }


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(DbUser).filter(DbUser.username == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Username not found."
        )

    if not Hash.verify(user.password, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Password."
        )

    access_token = create_access_token(data={"username": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "messaage": "Sucessfully  logged in",
    }


Algorithm = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTE = 30
Secret_key = "38c0763ddfbceb168c404c3c27b4155059c5d81386e3023c8643584bf9970074"


def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta

    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTE
        )
    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, Secret_key, algorithm=Algorithm)
    return encode_jwt


def get_current_user(
    token: str = Depends(oAuth2),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Secret_key, algorithms=[Algorithm])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(DbUser).filter(DbUser.username == username).first()
    if user is None:
        raise credentials_exception
    return user
