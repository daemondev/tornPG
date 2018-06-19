from sqlalchemy import ForeignKey, String, Integer, Date, Column, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('postgresql://termux:123@localhost/termux')
Base = declarative_base()

class Base(Base):
    __tablename__ = 'base'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), index=True)
    direccion = Column(String(200), index=True)
    telefono = Column(String(200), index=True)
    usuario = Column(String(200), index=True)

Base.metadata.create_all(engine)
