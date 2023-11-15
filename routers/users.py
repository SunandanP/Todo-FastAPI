from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from .auth import getDB, get_current_user, bcrypt_context, hashPassword, User

router = APIRouter(
    prefix="/user",
    tags=["users"],
    responses={404: {
        "User": "Doesn't exist"
    }}
)


@router.post("/create_user/")
async def create_user(user: User, db: Session = Depends(getDB)):
    user_model = models.User()
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


@router.get("/all")
async def get_users(db: Session = Depends(getDB)):
    return db.query(models.User).all()


@router.get("/{username}")
async def get_user_by_name(username: str, db: Session = Depends(getDB)):
    result = db.query(models.User).filter(models.User.username == username).first()
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.get("/")
async def get_user_by_id(id: int, db: Session = Depends(getDB)):
    result = db.query(models.User).filter(models.User.id == id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.put("/change_password")
async def change_password(current_password: str, new_password: str, db: Session = Depends(getDB),
                          user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        result: models.User = (db.query(models.User).filter(models.User.id == user.get("user_id")).first())
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
async def delete_user(username: str, db: Session = Depends(getDB), user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        result = (db.query(models.User).filter(models.User.id == user.get("user_id")))
        if result is not None:
            result.delete()
            db.commit()

            return {
                "status": 201,
                "detail": "User deleted Successfully!"
            }
        raise HTTPException(status_code=404, detail="User not found")
