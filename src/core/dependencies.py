from fastapi import Depends
from sqlalchemy.orm import Session

from database import SessionLocal


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBDependency: Session = Depends(get_db)
