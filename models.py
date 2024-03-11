from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from database import Base


class User(Base):
    __tablename__ = "users"

    User_pk = Column(Integer, primary_key=True, index=True)
    ID = Column(String, unique=True, index=True)
    PWD = Column(String, nullable=False)
    Phone = Column(String, nullable=False)
    Date = Column(DateTime, nullable=False)

class Detect(Base):
    __tablename__ = "detect"

    Detect_pk = Column(Integer, primary_key=True, index=True)
    User_pk = Column(Integer, ForeignKey("users.User_pk"))
    Label = Column(String, nullable=True)
    Record = Column(Text, nullable=True)
    Date = Column(DateTime, nullable=False)

class ALL(Base):
    __tablename__ = "all"

    ALL_pk = Column(Integer, primary_key=True, index=True)
    ALL_Cnt = Column(Integer, nullable=False)
    Detect_Cnt = Column(Integer, nullable=False)