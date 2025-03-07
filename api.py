from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from solver import solver_manager
from domain import TaskSchedule, Worker, Task
from datetime import datetime
from uuid import uuid4
from time import sleep

app = FastAPI()
data_sets: dict[str, TaskSchedule] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
start = datetime(2025, 2, 21, 9, 0)
end = datetime(2025, 2, 21, 11, 0)

test_schedule = TaskSchedule(
    workers=[
        Worker(name="Alice", skills={"plumbing"}, work_start_hour=8, work_end_hour=17),
        Worker(name="Bob", skills={"carpentry"}, work_start_hour=9, work_end_hour=18),
    ],
    tasks=[
        Task(id="1", required_skill="plumbing", location="Site A", priority="High",
             start=datetime(2025, 2, 21, 9, 0), end=datetime(2025, 2, 21, 11, 0)),
        Task(id="2", required_skill="carpentry", location="Site B", priority="Low",
             start=datetime(2025, 2, 21, 14, 0), end=datetime(2025, 2, 21, 16, 0)),
    ]
)

@app.post("/solve")
async def get_solved_schedule(schedule: TaskSchedule):
    job_id = str(uuid4())
    data_sets[job_id] = schedule
    solver_manager.solve(job_id, schedule, lambda solution: update_schedule(job_id, solution))

    stop_solver(job_id)
    
    return job_id

def update_schedule(problem_id: str, schedule: TaskSchedule):
    global data_sets
    data_sets[problem_id] = schedule

def stop_solver(job_id: str):
    sleep(1000)
    solver_manager.terminate_early(job_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
