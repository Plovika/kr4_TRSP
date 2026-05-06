from itertools import count
from threading import Lock

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="Task 11.1 - unit tests")

db: dict[int, dict] = {}
_id_seq = count(start=1)
_id_lock = Lock()


def next_task_id() -> int:
    with _id_lock:
        return next(_id_seq)


def reset_state() -> None:
    global _id_seq
    db.clear()
    _id_seq = count(start=1)


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=255)


class TaskOut(TaskIn):
    id: int
    completed: bool


@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskIn) -> TaskOut:
    task_id = next_task_id()
    db[task_id] = {**task.model_dump(), "completed": False}
    return TaskOut(id=task_id, **db[task_id])


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks() -> list[TaskOut]:
    return [TaskOut(id=task_id, **payload) for task_id, payload in sorted(db.items())]


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int) -> TaskOut:
    task = db.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut(id=task_id, **task)


@app.put("/tasks/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int) -> TaskOut:
    task = db.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task["completed"] = True
    return TaskOut(id=task_id, **task)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    if db.pop(task_id, None) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
