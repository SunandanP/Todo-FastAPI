from fastapi import Depends, HTTPException, APIRouter
from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import models
from passlib.context import CryptContext
from jose import jwt, JWTError
from database import localSession
from datetime import datetime, timedelta

SECRET_KEY = "You can never guess"
ALGORITHM = "HS256"


class User(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str


bcrypt_context = CryptContext(deprecated="auto", schemes=["bcrypt"])

o_auth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


def getDB():
    try:
        db = localSession()
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401 : {"User": "Not authorized"}}
)


def create_access_token(username: str, user_id: int, expires_in: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_in:
        expire = datetime.utcnow() + expires_in
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    encode.update({"exp" : expire})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


@router.post("/tokens")
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(getDB)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=404, detail="User doesn't exist or details mismatched")
    else:
        expiry = timedelta(minutes=20)
        token = create_access_token(user.username, user.id, expiry)
        return {"token" : token}

async def get_current_user(token : str = Depends(o_auth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get("sub")
        user_id : int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail="User doesn't exist")
        return {"username" : username, "user_id" : user_id}
    except JWTError :
        raise HTTPException(status_code=404, detail="User doesn't exist")


def verify_password(password: str, hashed_password: str):
    return bcrypt_context.verify(password, hashed_password)


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def hashPassword(password):
    return bcrypt_context.hash(password)
