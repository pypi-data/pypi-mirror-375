from enum import Enum
from typing import Any

import json5
from pydantic import BaseModel
from util_common.path import sort_paths

from workspace_services.settings import workspace_settings


class TaskType(str, Enum):
    CLASSIFICATION = "classification"
    DETECTION = "detection"


class Task(BaseModel):
    id: str
    task_type: TaskType
    description: str
    tag_config: dict[str, Any]


class TaskService:
    def __init__(self):
        self.task_root = workspace_settings.task_root
        self._tasks: dict[str, Task] = dict()

    @property
    def tasks(self) -> dict[str, Task]:
        if not self._tasks:
            self._load_tasks()
        return self._tasks

    def _read_task_settings(self, task_id: str) -> dict[str, Any]:
        task_settings_path = self.task_root / f"{task_id}.jsonc"
        if not task_settings_path.exists():
            raise ValueError(f"Task {task_id} not found")
        try:
            task_settings = json5.loads(task_settings_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to load task {task_id}: {e}")
        if (
            not isinstance(task_settings, dict)
            or "task_type" not in task_settings
            or "description" not in task_settings
            or "tag_config" not in task_settings
        ):
            raise ValueError(f"Invalid task settings for {task_id}")
        return task_settings

    def _get_task(self, task_id: str) -> Task:
        task_settings = self._read_task_settings(task_id)
        return Task(
            id=task_id,
            task_type=TaskType(task_settings["task_type"]),
            description=task_settings["description"],
            tag_config=task_settings["tag_config"],
        )

    def _load_tasks(self) -> dict[str, Task]:
        tasks: dict[str, Task] = dict()
        for task_path in sort_paths(self.task_root.glob('*.jsonc')):
            task_id = task_path.stem
            tasks[task_id] = self._get_task(task_id)
        self._tasks = tasks
        return tasks

    def get_task(self, task_id: str) -> Task:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        return self.tasks[task_id]


task_service = TaskService()
