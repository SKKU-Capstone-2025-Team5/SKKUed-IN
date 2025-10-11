from sqlalchemy.orm import declarative_base
from app.db.session import engine

Base = declarative_base()

def create_tables():
    # Import all models here so they are registered with Base
    from app.models.user import User  # noqa
    Base.metadata.create_all(bind=engine)
