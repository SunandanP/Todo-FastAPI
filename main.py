from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, localSession
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


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


@app.get("/todos")
async def get_all_todos(db: Session = Depends(getDB)):
    return db.query(models.Todo).all()


@app.get("/todos/{id}")
async def get_todo(id: int, db: Session = Depends((getDB))):
    todo = db.query(models.Todo).filter(models.Todo.id == id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail={
        "message": "Todo not found"
    })


@app.post("/todos/")
async def create_todo(todo: Todo, db: Session = Depends(getDB)):
    todo_model = models.Todo()
    todo_model.id = todo.id
    todo_model.title = todo.title
    todo_model.complete = todo.complete
    todo_model.priority = todo.priority
    todo_model.description = todo.description

    db.add(todo_model)
    db.commit()

    return {
        "status": 201,
        "detail": "Todo created Successfully!"
    }


@app.put("/todos/{id}")
async def update_todo(id: int, todo: Todo, db: Session = Depends(getDB)):
    todo_model = db.query(models.Todo).filter(models.Todo.id == id).first()

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

@app.delete("/todos/{id}")
async def delete_todo(id : int, db : Session = Depends(getDB)):
    result = db.query(models.Todo).filter(models.Todo.id == id)
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
