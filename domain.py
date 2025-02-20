from datetime import date, datetime
from typing import List, Optional, Set
#from timefold.solver.domain import *
from timefold.solver.domain._annotations import planning_solution
from timefold.solver.domain import planning_entity
from timefold.solver import SolverStatus
from timefold.solver.score import *
from timefold.solver.score import HardSoftDecimalScore
from pydantic import Field
from json_helper import JsonDomainBase
#from json_serialization import *

class Worker(JsonDomainBase):
    name: str
    skills: Set[str] = Field(default_factory=set)
    work_start_hour: int
    work_end_hour: int
    unavailable_dates: Set[date] = Field(default_factory=set)
    undesired_dates: Set[date] = Field(default_factory=set)

@planning_entity
class Task(JsonDomainBase):
    id: str
    required_skill: str
    location: str
    worker: Optional[Worker] = Field(default=None)
    start: datetime
    end: datetime

@planning_solution
class TaskSchedule(JsonDomainBase):
    workers: List[Worker] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    score: Optional[HardSoftDecimalScore] = Field(default=None)
    solver_status: Optional[SolverStatus] = Field(default=None)
