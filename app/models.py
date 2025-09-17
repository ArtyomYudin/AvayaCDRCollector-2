from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AvayaCDR(Base):
    __tablename__ = "avaya_cdr"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    calling_number = Column(String(64))
    called_number = Column(String(64))
    call_code = Column(String(64))
