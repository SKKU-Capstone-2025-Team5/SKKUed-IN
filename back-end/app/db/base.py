# app/db/base.py
from sqlalchemy.orm import declarative_base
Base = declarative_base()

def create_tables():
    # 순환참조 방지를 위해 함수 안에서 임포트
    from app.db.session import engine
    import app.models.user          # noqa: F401
    import app.models.team          # noqa: F401
    import app.models.contest       # noqa: F401
    import app.models.message       # noqa: F401
    import app.models.notification  # noqa: F401
    import app.models.skill         # noqa: F401   # <- 추가
    import app.models.interest      # noqa: F401   # <- 추가

    Base.metadata.create_all(bind=engine)

'''
#from sqlalchemy.orm import declarative_base
from app.db.base_class import Base
from app.db.session import engine
#
#from app.db.base_class import Base
from app.models.user import User
from app.models.team import Team
from app.models.contest import Contest
from app.models.message import Message
from app.models.notification import Notification
#from app.models import interaction 

#Base = declarative_base()

def create_tables():
    from app.models.user import User  # noqa
    Base.metadata.create_all(bind=engine)

'''