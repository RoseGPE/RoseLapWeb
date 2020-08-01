from sqlalchemy import (
  Column, 
  Integer,
  String,
  Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker
import json
import os
import hashlib
import base64

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  id       = Column(Integer, primary_key=True)
  name     = Column(String, nullable=False, unique=True)
  password = Column(String, nullable=True,  unique=False)
  salt     = Column(String, nullable=False, unique=False)

  def __init__(self, name, password):
    self.name = name
    self.salt = base64.b16encode(os.urandom(16))
    self.password = hashlib.sha1(bytes(password, 'utf-8')+self.salt).hexdigest()

  def check_password(self, password):
    return hashlib.sha1(bytes(password, 'utf-8')+self.salt).hexdigest() == self.password

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Study(Base):
  __tablename__ = 'study'
  id              = Column(Integer, primary_key=True)
  # 0->1->2->3/4 Drafting, Submitted, Running, Failed, Success
  status          = Column(Integer, nullable=False, unique=False)
  name            = Column(String,  nullable=False, unique=False)
  version         = Column(Integer, nullable=False, unique=False)
  runs_total      = Column(Integer, nullable=True,  unique=False)
  runs_complete   = Column(Integer, nullable=True,  unique=False)
  filedata        = Column(String,  nullable=False, unique=False)
  edit_date       = Column(String,  nullable=False, unique=False)
  submission_date = Column(String,  nullable=True,  unique=False)
  completion_date = Column(String,  nullable=True,  unique=False)
  log             = Column(String,  nullable=True,  unique=False)

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Vehicle(Base):
  __tablename__ = 'vehicle'
  id              = Column(Integer, primary_key=True)
  version         = Column(Integer, nullable=False, unique=False)
  name            = Column(String,  nullable=False, unique=False)
  filedata        = Column(String,  nullable=False, unique=False)
  edit_date       = Column(String,  nullable=False, unique=False)
  log             = Column(String,  nullable=True,  unique=False)
  status          = Column(Integer, nullable=False, unique=False)

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Track(Base):
  __tablename__ = 'track'
  id              = Column(Integer, primary_key=True)
  version         = Column(Integer, nullable=False, unique=False)
  name            = Column(String,  nullable=False, unique=False)
  filetype        = Column(String,  nullable=False, unique=False)
  filedata        = Column(String,  nullable=False, unique=False)
  unit            = Column(String,  nullable=False, unique=False)
  edit_date       = Column(String,  nullable=False, unique=False)
  log             = Column(String,  nullable=True,  unique=False)
  status          = Column(Integer, nullable=False, unique=False)

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

CONN_STRING = 'sqlite:///database.db'

engine = create_engine(CONN_STRING)

# Now we are ready to use the model

# new_user = User(name='admi')
# session.add(new_user)
# session.commit()

if __name__ == "__main__":
  Base.metadata.create_all(engine) # here we create all tables