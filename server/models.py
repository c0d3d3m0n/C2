from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=generate_uuid)
    hostname = Column(String)
    ip = Column(String)
    os = Column(String)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")

    tasks = relationship("Task", back_populates="agent")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.id"))
    command = Column(String)
    arguments = Column(String, nullable=True)
    status = Column(String, default="queued") # queued, sent, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="tasks")
    result = relationship("Result", back_populates="task", uselist=False)

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    output = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="result")
