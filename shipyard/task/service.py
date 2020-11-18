"""
Business logic for task related operations.
"""

from io import BytesIO
from typing import List

import gridfs
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from shipyard.crane.remove import remove_task
from shipyard.db import db
from shipyard.errors import AlreadyPresent, NotFound
from shipyard.node.model import Node
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

        Raises a `NotFound` error if no task is found with the given ID.
        """

        result = db.tasks.find_one({'_id': ObjectId(task_id)})
        if result is None:
            raise NotFound('No task found with the given ID.')
        return Task.Schema().load(result)

    @staticmethod
    def get_by_name(task_name: str) -> Task:
        """
        Fetch a task from the database by its name.

        Raises a `NotFound` error if no task is found with the given name.
        """

        result = db.tasks.find_one({'name': task_name})
        if result is None:
            raise NotFound('No task found with the given name.')
        return Task.Schema().load(result)

    @staticmethod
    def create(new_task: Task, file_name: str, file_body: BytesIO) -> str:
        """
        Insert a new task into the database.

        If the name of the new task is already in use, this method raises an
        `AlreadyPresent` error. If not, the new task is inserted and its new ID
        is returned.
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
    def update(task_id: str, new_values: dict, file_name: str, file_body: BytesIO) -> Task:
        """
        Updates an existing task.

        The task is retrieved using the given ID and updated with the values
        specified in the given dictionary. If a new file is also given, it
        replaces the old one. Returns the updated task.

        If no task is found with the given ID, raises a `NotFound` exception.
        """

        task = db.tasks.find_one({'_id': ObjectId(task_id)})
        if task is None:
            raise NotFound('No task found with the given ID.')

        if file_body:
            old_file_id = task['file_id']
            new_file_id = fs.put(file_body, filename=file_name)
            new_values = {**new_values, 'file_id': new_file_id}

        updated_task = db.tasks.find_one_and_update(
            {'_id': task['_id']},
            {'$set': new_values},
            return_document=ReturnDocument.AFTER
        )

        if file_body:
            fs.delete(old_file_id)

        nodes = db.nodes.find({'tasks._id': task['_id']})
        if nodes:
            for node in nodes:
                remove_task(task['name'], Node.Schema().load(node))
                db.nodes.update_one(
                    {'_id': node['_id']},
                    {'$pull': {'tasks': {'_id': task['_id']}}}
                )

        return Task.Schema().load(updated_task)

    @staticmethod
    def delete(task_id: str) -> Task:
        """
        Removes the task with the given ID from the database.

        Returns the task that has been deleted. If no task is found with the
        given ID, this method raises a `NotFound` error.
        """

        task = db.tasks.find_one({'_id': ObjectId(task_id)})
        if task is None:
            raise NotFound('No task found with the given ID.')

        db.tasks.delete_one({'_id': task['_id']})
        fs.delete(task['file_id'])

        nodes = db.nodes.find({'tasks._id': task['_id']})
        if nodes:
            for node in nodes:
                remove_task(task['name'], Node.Schema().load(node))
                db.nodes.find_one_and_update(
                    {'_id': node['_id']},
                    {'$pull': {'tasks': {'_id': task['_id']}}}
                )

        return Task.Schema().load(task)
