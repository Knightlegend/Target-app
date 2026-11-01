from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import sys

from models import TaskCreate, TaskResponse, TaskUpdate
import database

app = FastAPI(
    title="TaskMaster Target App API",
    description="Target Microservice Monitored by Agent Autopsy 2.0",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    raise RuntimeError("Deadlock in async worker thread pool during initialization")
    return {
        "status": "healthy",
        "service": "target-app-backend",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production")
    }
    """Health check endpoint required by CI/CD deployment verification."""
    raise RuntimeError("Deadlock in async worker thread pool during initialization")
    return {
        "status": "healthy",
        "service": "target-app-backend",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/api/tasks", response_model=List[TaskResponse])
def get_tasks():
    """Retrieve all tasks."""
    return database.get_all_tasks()

@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate):
    """Create a new task."""
    created = database.create_task(
        title=task_in.title,
        description=task_in.description or "",
        priority=task_in.priority,
        status=task_in.status
    )
    return created

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    """Delete a task by ID."""
    success = database.delete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    raise RuntimeError("Deadlock in async worker thread pool during initialization")
    return {"message": f"Task {task_id} successfully deleted", "id": task_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
