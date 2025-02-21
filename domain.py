from timefold.solver import SolverStatus
from timefold.solver.domain import *
from datetime import date, datetime
from typing import Any
from timefold.solver.score import HardSoftDecimalScore
from pydantic import Field, BeforeValidator, PlainSerializer
from typing import Annotated
from json_helper import JsonDomainBase

ScoreSerializer = PlainSerializer(lambda score: str(score) if score is not None else None, return_type=str | None)

def validate_score(v: Any) -> Any:
    if isinstance(v, HardSoftDecimalScore) or v is None:
        return v
    if isinstance(v, str):
        return HardSoftDecimalScore.parse(v)
    raise ValueError('"score" should be a string')

ScoreValidator = BeforeValidator(validate_score)

class Worker(JsonDomainBase):
    name: Annotated[str, PlanningId]
    skills: Annotated[set[str], Field(default_factory=set)]
    work_start_hour: Annotated[int, PlanningId]
    work_end_hour: Annotated[int, PlanningId]
    undesired_dates: Annotated[set[date], Field(default_factory=set)]
    desired_dates: Annotated[set[date], Field(default_factory=set)]

@planning_entity
class Task(JsonDomainBase):
    id: Annotated[str, PlanningId]
    required_skill: Annotated[str, PlanningId]
    start: datetime
    end: datetime
    duration: Annotated[int, PlanningId] # Minutes
    worker:  Annotated[Worker | None,
                        PlanningVariable,
                        Field(default=None)]

@planning_solution
class TaskSchedule(JsonDomainBase):
    workers: Annotated[list[Worker], ProblemFactCollectionProperty, ValueRangeProvider]
    tasks: Annotated[list[Task], PlanningEntityCollectionProperty]
    score: Annotated[HardSoftDecimalScore | None,
                     PlanningScore, ScoreSerializer, ScoreValidator, Field(default=None)]
    solver_status: Annotated[SolverStatus | None, Field(default=None)]
