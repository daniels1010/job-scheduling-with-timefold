from timefold.solver.score import (constraint_provider, ConstraintFactory, Joiners, HardSoftDecimalScore, ConstraintCollectors)
from datetime import datetime, date, timedelta
from domain import Worker, Task


@constraint_provider
def define_constraints():
    return  [
        # 1. Assign each task to only one employee
        "unique_task_assignment",

        # 2. Balance workload across employees
        "workload_balance",
    ]

'''
@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        ### Hard constraints
        unavailable_worker(constraint_factory), # C1
        worker_time_limit_constraints(constraint_factory), # C4
        required_skill(constraint_factory), # C5
        no_overlapping_tasks(constraint_factory), # C6

        ### Soft constraints
        undesired_day_for_worker(constraint_factory), # C2
        worker_overtime_constraints(constraint_factory), # C3
        balance_worker_task_assignments(constraint_factory) # Apkārtnes funkcija
    ]
'''


def required_skill(constraint_factory: ConstraintFactory):
    return (constraint_factory.for_each(Task)
            .filter(lambda shift: shift.required_skill not in shift.employee.skills)
            .penalize(HardSoftDecimalScore.ONE_HARD)
            .as_constraint("Missing required skill")
            )

def is_overlapping_with_date(task: Task, dt: date) -> bool:
    return task.start.date() == dt or task.end.date() == dt

def get_minute_overlap(task1: Task, task2: Task) -> int:
    return (min(task1.end, task2.end) - max(task1.start, task2.start)).total_seconds() // 60

def overlapping_in_minutes(first_start_datetime: datetime, first_end_datetime: datetime,
                           second_start_datetime: datetime, second_end_datetime: datetime) -> int:
    latest_start = max(first_start_datetime, second_start_datetime)
    earliest_end = min(first_end_datetime, second_end_datetime)
    delta = (earliest_end - latest_start).total_seconds() / 60
    return max(0, delta)

def get_task_overlapping_duration_in_minutes(task: Task, dt: date) -> int:
    overlap = 0
    start_date_time = datetime.combine(dt, datetime.max.time())
    end_date_time = datetime.combine(dt, datetime.min.time())
    overlap += overlapping_in_minutes(start_date_time, end_date_time, task.start, task.end)
    return overlap

def unavailable_worker(constraint_factory: ConstraintFactory):
    return (constraint_factory.for_each(Task)
            .join(Worker, Joiners.equal(lambda task: task.worker, lambda worker: worker))
            .flatten_last(lambda worker: worker.unavailable_dates)
            .filter(lambda task, unavailable_date: is_overlapping_with_date(task, unavailable_date))
            .penalize(HardSoftDecimalScore.ONE_HARD,
                      lambda task, unavailable_date: get_task_overlapping_duration_in_minutes(task,
                                                                                                unavailable_date))
            .as_constraint("Unavailable worker")
            )

def no_overlapping_tasks(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each_unique_pair(Task,
                                  Joiners.equal(lambda task: task.employee.name),
                                  Joiners.overlapping(lambda task: task.start, lambda task: task.end))
            .penalize(HardSoftDecimalScore.ONE_HARD, get_minute_overlap)
            .as_constraint("Overlapping shift")
            )

def undesired_day_for_worker(constraint_factory: ConstraintFactory):
    return (constraint_factory.for_each(Task)
            .join(Worker, Joiners.equal(lambda task: task.worker, lambda worker: worker))
            .flatten_last(lambda worker: worker.undesired_dates)
            .filter(lambda task, undesired_date: is_overlapping_with_date(task, undesired_date))
            .penalize(HardSoftDecimalScore.ONE_SOFT,
                      lambda task, undesired_date: get_task_overlapping_duration_in_minutes(task, undesired_date))
            .as_constraint("Undesired day for worker")
            )


def balance_worker_task_assignments(constraint_factory: ConstraintFactory):
    return (constraint_factory.for_each(Task)
            .group_by(lambda task: task.worker, ConstraintCollectors.count())
            .complement(Worker, lambda e: 0)  # Include all workers which are not assigned to any job.
            .group_by(ConstraintCollectors.load_balance(lambda worker, job_count: worker,
                                                        lambda worker, job_count: job_count))
            .penalize_decimal(HardSoftDecimalScore.ONE_SOFT, lambda load_balance: load_balance.unfairness())
            .as_constraint("Balance worker job assignments")
            )

def worker_time_limit_constraints(constraint_factory: ConstraintFactory):
    constraints = []
    constraints.append(
        constraint_factory.for_each(Task)
        .join(Task, lambda task1, task2: task1.worker == task2.worker and task1 != task2)  
        .filter(lambda task1, task2: abs((task1.start - task2.start).days) < 7)  
        .group_by(lambda task1: task1.worker, lambda task1: task1.start)
        .penalize(HardSoftDecimalScore.ONE_HARD, lambda task1, tasks: sum((task.end - task.start).total_seconds() / 3600 for task in tasks) > 80, 
                  "Worker can not exceed 80 hours in any 7-day period if possible")
    )

    return constraints

def worker_overtime_constraints(constraint_factory: ConstraintFactory):
    constraints = []
    constraints.append(
        constraint_factory.for_each(Task)
        .join(Task, lambda task1, task2: task1.worker == task2.worker and task1 != task2)  
        .filter(lambda task1, task2: abs((task1.start - task2.start).days) < 7)  
        .group_by(lambda task1: task1.worker, lambda task1: task1.start)
        .penalize(HardSoftDecimalScore.ONE_SOFT, lambda task1, tasks: sum((task.end - task.start).total_seconds() / 3600 for task in tasks) > 40, 
                  "Worker should not exceed 40 hours in any 7-day period if possible")
    )

    return constraints
