from sqlalchemy import Column, String, Integer, Boolean
from database import Base

class Todo(Base):
    __tablename__ = "Todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)