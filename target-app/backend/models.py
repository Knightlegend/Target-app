from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(default="", max_length=1000, description="Task description")
    priority: str = Field(default="medium", description="Priority: low, medium, high")
    status: str = Field(default="pending", description="Status: pending, in_progress, completed")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
