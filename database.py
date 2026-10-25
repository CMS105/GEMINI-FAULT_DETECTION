from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Initialize SQLite database engine
Base = declarative_base()
engine = create_engine("sqlite:///./events.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class EventRecord(Base):
    """Database table schema for persisting incoming webhooks and AI outputs."""
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    payload = Column(Text)
    status = Column(String)
    ai_analysis = Column(Text)

# Automatically create the events.db file and schema on startup
Base.metadata.create_all(bind=engine)