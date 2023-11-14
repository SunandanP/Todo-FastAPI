from fastapi import FastAPI, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import models
import models as md
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


app = FastAPI()

@app.get("/users")
async def get_all_users(db: Session = Depends(getDB)):
    return db.query(models.User).all()


@app.get("/users/{username}")
async def get_user(username: str, db: Session = Depends(getDB)):
    return db.query(models.User).filter(models.User.username == username).first()


@app.post("/users/create_user")
async def create_user(user: User, db: Session = Depends(getDB)):
    user_model = md.User()
    user_model.email = user.email
    user_model.username = user.username
    user_model.first_name = user.first_name
    user_model.last_name = user.last_name
    user_model.hashed_password = hashPassword(user.password)
    user_model.isActive = True

    db.add(user_model)
    db.commit()
    return {
        "status": 201,
        "detail": "User created Successfully!"
    }


def create_access_token(username: str, user_id: int, expires_in: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_in:
        expire = datetime.utcnow() + expires_in
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    encode.update({"exp" : expire})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


@app.post("/tokens")
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
