from fastapi import FastAPI
from routers import auth, todos, users
from companyapis import companyapis

app = FastAPI()
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(companyapis.router)

