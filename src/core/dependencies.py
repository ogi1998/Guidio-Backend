from fastapi import Depends
from sqlalchemy.orm import Session

from database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


DBDependency: Session = Depends(get_db)  # TODO: remove this when there is no usage
