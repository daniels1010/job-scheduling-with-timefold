from timefold.solver import SolverFactory, SolverManager, SolutionManager
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig, TerminationConfig, Duration)
from domain import Task, TaskSchedule
from constraints import define_constraints
#from model import Schedule

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

solver_manager = SolverManager.create(SolverFactory.create(solver_config))
solution_manager = SolutionManager.create(solver_manager)