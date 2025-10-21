from sqlalchemy.orm import declarative_base
from app.db.session import engine

Base = declarative_base()

def create_tables():
    from app.models.user import User  # noqa
    Base.metadata.create_all(bind=engine)
