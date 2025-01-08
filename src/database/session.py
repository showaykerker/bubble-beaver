from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
import logging
from ..models.base import Base
from ..models.artist import Artist
from ..models.message import Message

class DatabaseSession:
    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "bubble_beaver.db")
        
        try:
            self.engine = create_engine(f"sqlite:///{db_path}", echo=True)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.create_tables()
        except SQLAlchemyError as e:
            logging.error(f"Failed to initialize database: {str(e)}")
            raise
        
    def create_tables(self):
        try:
            Base.metadata.create_all(bind=self.engine)
        except SQLAlchemyError as e:
            logging.error(f"Failed to create tables: {str(e)}")
            raise
        
    def get_session(self) -> Session:
        try:
            return self.SessionLocal()
        except SQLAlchemyError as e:
            logging.error(f"Failed to create database session: {str(e)}")
            raise

db = DatabaseSession()
