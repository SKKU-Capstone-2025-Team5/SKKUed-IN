from sqlalchemy.orm import declarative_base
from app.db.session import engine
#
from app.db.base_class import Base
from app.models.user import User
from app.models.team import Team
from app.models.contest import Contest
from app.models.message import Message
from app.models.notification import Notification
#from app.models import interaction 

Base = declarative_base()

def create_tables():
    from app.models.user import User  # noqa
    Base.metadata.create_all(bind=engine)
