from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData, Table, Integer, String, Date, Column, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Book(Base):
    __tablename__ = 'Book_orm'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    published = Column(Integer)
    date_added = Column(DateTime, default=datetime.utcnow)
    date_deleted = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)



class Borrow(Base):
    __tablename__ = 'Borrow_orm'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('Book_orm.id'))
    user_id = Column(Integer)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    book = relationship("Book")

