from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.db.base import Base

class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    ex_name = Column(String, nullable=False)
    ex_link = Column(String, nullable=False, unique=True)
    ex_host = Column(String)
    ex_image = Column(String)
    ex_start = Column(Date)
    ex_end = Column(Date)
    ex_flag = Column(Integer)

    teams = relationship("Team", back_populates="contest")