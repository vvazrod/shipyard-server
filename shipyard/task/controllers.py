import json
import tarfile
import io
import ast

import hug

from bson.objectid import InvalidId
from marshmallow import ValidationError

from shipyard.errors import AlreadyPresent
from shipyard.task.service import TaskService
from shipyard.task.model import Task


@hug.get('/')
def get_task_list(response, name: str = None):
    """
    Retrieve the full list of tasks or a task with a given name.

    If the `name` parameter is specified in the request, this function attempts
    to return the task with that name. If it is not found, returns a 404
    response.

    If no name is given, the function returns the full list of tasks present in
    the system.
    """

    if name is not None:
        result = TaskService.get_by_name(name)
        if result is None:
            response.status = hug.HTTP_NOT_FOUND
            return {'error': 'Task not found with the given name.'}
        return Task.Schema().dump(result)

    results = TaskService.get_all()
    return Task.Schema(only=['_id', 'name', 'runtime', 'deadline', 'period']).dump(results, many=True)


@hug.post('/')
def post_task(body, response):
    """
    Create a new task resource.

    This function attempts to create a new task resource with the data given in
    the request in the form of a tar file. This tar file contains an
    `specs.json` file with the task's specification. The rest of the files of
    contained in the tarball are the source code of the task and its Dockerfile
    for deployment.

    If the operation is succesful, the new task's ID is returned. If the name
    for the new task is already in use, returns a 409 response. If the new
    task's specification data isn't correct, returns a 400 response.
    """

    file_name = body['file'][0]
    file_body = body['file'][1]
    specs = json.load(body['specs'][1])

    try:
        new_task = Task.Schema().load(specs)
        new_id = TaskService.create(new_task, file_name, file_body)
        return {'_id': new_id}
    except ValidationError as e:
        response.status = hug.HTTP_BAD_REQUEST
        return e.messages
    except AlreadyPresent as e:
        response.status = hug.HTTP_CONFLICT
        return {'error': str(e)}


@hug.get('/{task_id}')
def get_task(task_id: str, response):
    """
    Retrieve the task with the given ID.

    If no task is found, returns a 404 response. If the given ID is invalid,
    returns a 400 response.
    """

    try:
        result = TaskService.get_by_id(task_id)
        if result is None:
            response.status = hug.HTTP_NOT_FOUND
            return {'error': 'Task not found with the given ID.'}
        return Task.Schema().dump(result)
    except InvalidId:
        response.status = hug.HTTP_BAD_REQUEST
        return {'error': 'Invalid ID.'}


@hug.delete('/{task_id}')
def delete_task(task_id: str, response):
    """
    Delete the task with the given ID.

    Returns the deleted task's data in the response.

    If no task is found, returns a 404 response. If the given ID is invalid,
    returns a 400 response.
    """

    try:
        result = TaskService.delete(task_id)
        if result is None:
            response.status = hug.HTTP_NOT_FOUND
            return {'error': 'Task not found with the given ID.'}
        return Task.Schema(exclude=['_id', 'file_id']).dump(result)
    except InvalidId:
        response.status = hug.HTTP_BAD_REQUEST
        return {'error': 'Invalid ID.'}
