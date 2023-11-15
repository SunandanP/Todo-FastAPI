from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, Request
import models
from database import engine, localSession
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routers.auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    tags=["todos"],
    responses={404 : {"Todo": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

class Todo(BaseModel):
    id: int = Field()
    title: str = Field()
    description: Optional[str] = Field()
    priority: int = Field()
    complete: bool = Field()


def getDB():
    try:
        db = localSession()
        yield db
    finally:
        db.close()

def user_not_found(user):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/test")
async def get_test(request : Request):
    return templates.TemplateResponse("register.html", {"request": request})

# particular todos
@router.get("/todo/")
async def get_user_todo(id: int, db : Session = Depends(getDB), user = Depends(get_current_user)):
    user_not_found(user)
    response = db.query(models.Todo).filter(models.Todo.owner_id == user.get("user_id")).filter( models.Todo.id == id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    return response

# all todos
@router.get("/")
async def get_user_todos(db : Session = Depends(getDB), user = Depends(get_current_user)):
    user_not_found(user)
    return db.query(models.Todo).filter(models.Todo.owner_id == user.get("user_id")).all()

# create new todo

@router.post("/")
async def create_todo(todo: Todo, db: Session = Depends(getDB), user = Depends(get_current_user)):
    user_not_found(user)
    todo_model = models.Todo()
    todo_model.title = todo.title
    todo_model.complete = todo.complete
    todo_model.priority = todo.priority
    todo_model.description = todo.description
    todo_model.owner_id = user.get("user_id")

    db.add(todo_model)
    db.commit()

    return {
        "status": 201,
        "detail": "Todo created Successfully!"
    }

# update todo
@router.put("/todo/")
async def update_todo(id: int, todo: Todo, db: Session = Depends(getDB), user = Depends(get_current_user)):
    response = db.query(models.Todo).filter(models.Todo.owner_id == user.get("user_id")).filter( models.Todo.id == id).first()
    user_not_found(user)
    if response is None:
        raise HTTPException(status_code=404, detail="todo not found")
    todo_model = response
    todo_model.title = todo.title
    todo_model.complete = todo.complete
    todo_model.priority = todo.priority
    todo_model.description = todo.description

    db.add(todo_model)
    db.commit()
    return {
        "status": 200,
        "detail": "Todo updated Successfully!"
    }

@router.delete("/todo/")
async def delete_todo(id : int, db : Session = Depends(getDB), user = Depends(get_current_user)):
    result = db.query(models.Todo).filter(models.Todo.id == id).filter(models.Todo.owner_id == user.get("user_id"))
    if result is not None:
        result.delete()
        db.commit()
        return {
            "status": 200,
            "detail": "Todo deleted Successfully!"
        }

    raise_http_exception()
def raise_http_exception():
    raise HTTPException(status_code=404, detail="Todo not found!")
