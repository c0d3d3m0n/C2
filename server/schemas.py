from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Agent Schemas
class AgentBase(BaseModel):
    hostname: str
    ip: str
    os: str

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: str
    last_seen: datetime
    status: str

    class Config:
        orm_mode = True

# Task Schemas
class TaskBase(BaseModel):
    command: str
    arguments: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    agent_id: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

# Result Schemas
class ResultBase(BaseModel):
    task_id: int
    output: str

class ResultCreate(ResultBase):
    pass

class Result(ResultBase):
    id: int
    executed_at: datetime

    class Config:
        orm_mode = True
