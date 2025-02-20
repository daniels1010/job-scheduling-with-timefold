from pydantic import BaseModel
from typing import List, Optional

class Worker(BaseModel):
    id: int
    name: str

class Task(BaseModel):
    id: int
    name: str
    duration: int  
    required_worker: Optional[int]  

class Schedule(BaseModel):
    workers: List[Worker]
    tasks: List[Task]