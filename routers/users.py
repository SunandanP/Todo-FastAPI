from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from .auth import getDB, get_current_user, bcrypt_context

router = APIRouter(
    prefix="/user",
    tags=["users"],
    responses={404: {
        "User": "Doesn't exist"
    }}
)


@router.get("/all")
async def get_users(db: Session = Depends(getDB)):
    return db.query(User).all()


@router.get("/{username}")
async def get_user_by_name(username: str, db: Session = Depends(getDB)):
    result = db.query(User).filter(User.username == username).first()
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@router.get("/")
async def get_user_by_id(id: int, db: Session = Depends(getDB)):
    result = db.query(User).filter(User.id == id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@router.put("/change_password")
async def change_password(current_password: str, new_password: str, db : Session = Depends(getDB), user = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        result : User = (db.query(User).filter(User.id == user.get("user_id")).first())
        if bcrypt_context.verify(current_password, result.hashed_password):
            if bcrypt_context.verify(new_password, result.hashed_password):
                raise HTTPException(status_code=400, detail="old password cannot be a new password")
            result.hashed_password = bcrypt_context.hash(new_password)
            db.add(result)
            db.commit()

            return {
                "status": 201,
                "detail": "Password updated Successfully!"
            }
        raise HTTPException(status_code=401, detail="Old password didn't match")

@router.delete("/{username}")
async def delete_user(username : str, db : Session = Depends(getDB), user = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        result = (db.query(User).filter(User.id == user.get("user_id")))
        if result is not None:
            result.delete()
            db.commit()

            return {
                "status": 201,
                "detail": "User deleted Successfully!"
            }
        raise HTTPException(status_code=404, detail="User not found")
