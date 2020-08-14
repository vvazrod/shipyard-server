import hug

from bson.objectid import InvalidId
from marshmallow import ValidationError

from shipyard.errors import NotFound, NotFeasible, MissingDevices
from shipyard.node.service import NodeService
from shipyard.node.model import Node


@hug.get('/')
def get_node_list(response, name: str = None):
    """
    Retrieve the full list of nodes or a node with a given name.

    If the `name` parameter is specified in the request, this function attempts
    to return the node with that name. If it is not found, returns a 404
    response.

    If no name is given, the function returns the full list of nodes present in
    the system.
    """

    if name is not None:
        result = NodeService.get_by_name(name)
        if result is None:
            response.status = hug.HTTP_NOT_FOUND
            return {'error': 'Node not found with the given name.'}
        return Node.Schema().dump(result)

    results = NodeService.get_all()
    return Node.Schema(only=['_id', 'name', 'ip', 'cpu', 'cpu_arch']).dump(results, many=True)


@hug.post('/')
def post_node(body, response):
    """
    Create a new node resource.

    This function attempts to create a new node resource with the data given in
    the body of the request, returning its new ID in the response.

    If the name for the new node is already in use, returns a 409 response. If
    the new node's data isn't correct, returns a 400 response.
    """

    try:
        new_node = Node.Schema().load(body)
        new_id = NodeService.create(new_node)
        return {'_id': new_id}
    except ValidationError as validation_err:
        response.status = hug.HTTP_BAD_REQUEST
        return validation_err.messages
    except ValueError:
        response.status = hug.HTTP_CONFLICT
        return {'error': 'A node already exists with the given name.'}


@hug.get('/{node_id}')
def get_node(node_id: str, response):
    """
    Retrieve the node with the given ID.

    If no node is found, returns a 404 response. If the given ID is invalid,
    returns a 400 response.
    """

    try:
        result = NodeService.get_by_id(node_id)
        if result is None:
            response.status = hug.HTTP_NOT_FOUND
            return {'error': 'Node not found with the given ID.'}
        return Node.Schema().dump(result)
    except InvalidId:
        response.status = hug.HTTP_BAD_REQUEST
        return {'error': 'Invalid ID.'}


@hug.delete('/{node_id}')
def delete_node(node_id: str, response):
    """
    Delete the node with the given ID.

    Returns the deleted node's data in the response.

    If no node is found, returns a 404 response. If the given ID is invalid,
    returns a 400 response.
    """
    try:
        result = NodeService.delete(node_id)
        if result is None:
            response.status = hug.HTTP_NOT_FOUND
            return {'error': 'Node not found with the given ID.'}
        return Node.Schema(exclude=['_id']).dump(result)
    except InvalidId:
        response.status = hug.HTTP_BAD_REQUEST
        return {'error': 'Invalid ID.'}


@hug.post('/{node_id}/tasks')
def post_node_tasks(node_id: str, response, task_id: str = None):
    """
    Add a task to a node using their IDs.

    Returns the updated node's data in the response.

    If no task ID is present in the request or any ID is invalid, returns a 400
    response.

    If no node or task are found with the given IDs, returns a 404 response.

    If the operation can't be finished, returns a 500 response.
    """

    if task_id is None:
        response.status = hug.HTTP_BAD_REQUEST
        return {'error': 'No task ID was specified in the request'}

    try:
        result = NodeService.add_task(node_id, task_id)
        if result is None:
            response.status = hug.HTTP_INTERNAL_SERVER_ERROR
            return {'error': 'Unable to add task to node'}
        return Node.Schema().dump(result)
    except InvalidId as e:
        response.status = hug.HTTP_BAD_REQUEST
        return {'error': str(e)}
    except NotFound as e:
        response.status = hug.HTTP_NOT_FOUND
        return {'error': str(e)}
    except NotFeasible as e:
        response.status = hug.HTTP_INTERNAL_SERVER_ERROR
        return {'error': str(e)}
    except MissingDevices as e:
        response.status = hug.HTTP_INTERNAL_SERVER_ERROR
        return {'error': str(e)}


@hug.delete('/{node_id}/tasks/{task_id}')
def delete_node_tasks(node_id: str, task_id: str, response):
    """
    Remove a task from a node's taskset.

    Returns the updated node's data in the response.

    If no task ID is present in the request or any ID is invalid, returns a 400
    response.

    If no node or task are found with the given IDs, returns a 404 response.

    If the operation can't be finished, returns a 500 response.
    """

    try:
        result = NodeService.remove_task(node_id, task_id)
        if result is None:
            response.status = hug.HTTP_INTERNAL_SERVER_ERROR
            return {'error': 'Unable to add task to node'}
        return Node.Schema().dump(result)
    except InvalidId as e:
        response.status = hug.HTTP_BAD_REQUEST
        return {'error': str(e)}
    except NotFound as e:
        response.status = hug.HTTP_NOT_FOUND
        return {'error': str(e)}
