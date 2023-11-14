from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@127.0.0.1:3306/todo"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
localSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()
