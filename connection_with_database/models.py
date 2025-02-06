from sqlalchemy import Table, Column, Integer, String
# from database import Base
from connection_with_database.database import Base

class Books(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    description = Column(String)
    rating = Column(Integer)
