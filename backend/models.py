from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email_type = Column(String(50), default='professional')  # 'professional' or 'career'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship("ChatSession", back_populates="messages")

class NewsletterSchedule(Base):
    __tablename__ = 'newsletter_schedules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    template_content = Column(Text, nullable=False)
    recipient_group = Column(String(255), nullable=False)
    frequency = Column(String(50), nullable=False)  # 'monthly', 'weekly', etc.
    next_send_date = Column(DateTime, nullable=False)
    last_sent_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create SQLite database
engine = create_engine('sqlite:///./newsletter.db', echo=True)
Base.metadata.create_all(engine) 