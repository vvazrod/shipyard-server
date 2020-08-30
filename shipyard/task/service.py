import gridfs

from typing import List
from io import BytesIO

from bson.objectid import ObjectId

from shipyard.db import db
from shipyard.errors import AlreadyPresent
from shipyard.task.model import Task


fs = gridfs.GridFS(db)


class TaskService():
    """Task business logic."""

    @staticmethod
    def get_all() -> List[Task]:
        """Fetch all tasks from the database."""

        return Task.Schema().load(db.tasks.find(), many=True)

    @staticmethod
    def get_by_id(task_id: str) -> Task:
        """
        Fetch a task from the database by its ID.

        Returns `None` if no task is found with the given ID.
        """

        result = db.tasks.find_one({'_id': ObjectId(task_id)})
        if result is None:
            return None
        return Task.Schema().load(result)

    @staticmethod
    def get_by_name(task_name: str) -> Task:
        """
        Fetch a task from the database by its name.

        Returns `None` if no tasks is found with the given name.
        """

        result = db.tasks.find_one({'name': task_name})
        if result is None:
            return None
        return Task.Schema().load(result)

    @staticmethod
    def create(new_task: Task, file_name: str, file_body: BytesIO) -> str:
        """
        Insert a new task into the database.

        If the name of the new task is already in use, this method raises a
        `ValueError`. If not, the new task is inserted and its new ID is
        returned.
        """

        result = db.tasks.find_one({'name': new_task.name})
        if result is not None:
            raise AlreadyPresent('A task already exists with the given name.')

        file_id = fs.put(file_body, filename=file_name)
        new_task.file_id = file_id

        new_id = db.tasks.insert_one(Task.Schema(
            exclude=['_id']).dump(new_task)).inserted_id
        return str(new_id)

    @staticmethod
    def delete(task_id: str) -> Task:
        """
        Removes the task with the given ID from the database.

        Returns the task that has been deleted. If no task is found with the
        given ID, this method returns `None`.
        """

        result = db.tasks.find_one_and_delete({'_id': ObjectId(task_id)})
        if result is None:
            return None
        fs.delete(ObjectId(result['file_id']))
        return Task.Schema().load(result)
