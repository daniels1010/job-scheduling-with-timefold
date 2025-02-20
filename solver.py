from timefold.solver import SolverFactory
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig, TerminationConfig, Duration)
from domain import Task, Worker, TaskSchedule
from model import Schedule

def define_constraints():
    return [
        # 1. Assign each task to only one employee
        "unique_task_assignment",

        # 2. Balance workload across employees
        "workload_balance",
    ]

def solve_schedule(schedule: Schedule):
    # Timefold configuration
    solver_config = SolverConfig(
        solution_class=TaskSchedule,
        entity_class_list=[Task],
        score_director_factory_config=ScoreDirectorFactoryConfig(
            constraint_provider_function=define_constraints
        ),
        termination_config=TerminationConfig(
            spent_limit=Duration(seconds=30)
        )
    )

    print('DEBUG CONF ', solver_config)
    print(TaskSchedule.__module__)

    solver_factory = SolverFactory.create(solver_config)
    solver = solver_factory.build_solver()
    
    # Solve the scheduling problem
    solved_schedule = solver.solve(schedule)
    return solved_schedule
