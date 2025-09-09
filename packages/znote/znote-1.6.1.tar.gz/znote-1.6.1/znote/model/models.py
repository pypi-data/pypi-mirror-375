from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

# Base class for declarative models
Base = declarative_base()

# Define the models
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    workspace = Column(String, nullable=False, default="default")
    active_workspace = Column(String, nullable=False, default="default")

class Note(Base):
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    creator_id = Column(Integer, nullable=False)
    editor_id = Column(Integer, nullable=False)
    protected = Column(String, nullable=True)
    shared_with = Column(String, nullable=True, default="")  # Liste d’IDs ou noms d’utilisateurs
    workspace = Column(String, nullable=False)

class Channel(Base):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)  # Nom du canal
    description = Column(String, nullable=True)
    channel_hash = Column(String, nullable=False)       # Dernier hash publié
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    creator_id = Column(Integer, nullable=False)         # ID de l'utilisateur qui a créé le canal

class PubChannel(Base):
    __tablename__ = 'pubchannel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, nullable=False)         # ID du canal (référence manuelle)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)