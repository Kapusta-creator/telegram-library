from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, MetaData, desc
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
from .models import *
user = "thatttar"

connection_string = f"postgresql+psycopg2://{user}:@localhost:5432/{user}"


class DatabaseConnector:

    def __init__(self):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add(self, title, author, published):
        try:
            book = Book(title=title.lower(), author=author.lower(), published=published)
            self.session.add(book)
            self.session.commit()
            return book.id
        except Exception as e:
            print(e)
            self.session.rollback()
            return False

    def delete(self, book_id):
        try:
            borrow = self.session.query(Borrow).filter_by(book_id=book_id).order_by(desc(Borrow.start_time)).first()
            if borrow and borrow.end_time is None:
                return False
            else:
                book = self.session.query(Book).filter_by(id=book_id).first()
                book.is_active = False
                book.date_deleted = datetime.utcnow()
                self.session.commit()
                return True
        except:
            self.session.rollback()
            return False

    def list_books(self):
        try:
            books = self.session.query(Book).all()
            if len(books) == 0:
                return None
            return [(book.title, book.author, book.published, book.is_active) for book in books]
        except:
            return None

    def get_book(self, title, author):
        try:
            book = self.session.query(Book).filter_by(title=title.lower(), author=author.lower(), is_active=True).first()
            if book:
                return book.id
            else:
                return None
        except:
            return None

    def borrow(self, book_id, user_id):
        try:
            borrow = self.session.query(Borrow).filter_by(user_id=user_id).order_by(desc(Borrow.start_time)).first()
            if borrow and borrow.end_time is None:
                return False
            else:
                borrow = self.session.query(Borrow).filter_by(book_id=book_id, end_time=None).first()
                if borrow:
                    return False
                else:
                    start_time = datetime.utcnow()
                    borrow = Borrow(book_id=book_id, user_id=user_id, start_time=start_time)
                    self.session.add(borrow)
                    self.session.commit()
                    return borrow.id
        except Exception as e:
            print(e)
            self.session.rollback()
            return False

    def get_borrow(self, user_id):
        try:
            borrow = self.session.query(Borrow).filter_by(user_id=user_id, end_time=None).first()
            if borrow:
                return borrow.id
            else:
                return None
        except:
            return None

    def retrieve(self, user_id):
        try:
            end_time = datetime.utcnow()
            borrow = self.session.query(Borrow).filter_by(user_id=user_id).order_by(desc(Borrow.start_time)).first()
            if borrow and borrow.end_time is None:
                borrow.end_time = end_time
                self.session.commit()
                return [borrow.book.title, borrow.book.author, str(borrow.book.published)]
            return []
        except Exception as e:
            print(e)
            self.session.rollback()
            return []

    def __del__(self):
        self.session.close()
