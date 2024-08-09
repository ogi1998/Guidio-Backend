from fastapi import Depends
from sqlalchemy.orm import Session

from database import SessionLocal


class DBSession:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


def get_db() -> Session:
    with DBSession() as db:
        yield db


DBDependency: Session = Depends(get_db)
