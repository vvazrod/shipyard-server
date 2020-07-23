import hug

from bson.objectid import InvalidId

from .service import NodeService
from .model import Node


@hug.get('')
def get_node_list(response, name: str = None):
    if name is not None:
        result = NodeService.get_by_name(name)
        if result is None:
            response.status = hug.HTTP_NOT_FOUND
            return {'msg': 'Node not found with the given name.'}
        return Node.Schema().dump(result)

    results = NodeService.get_all()
    return Node.Schema(only=["_id", "name", "ip", "cpu", "cpu_arch"]).dump(results, many=True)


@hug.post('')
def post_node(body, response):
    try:
        new_node = Node.Schema().load(body)
        new_id = NodeService.create(new_node)
        return {'_id': new_id}
    except ValueError:
        response.status = hug.HTTP_CONFLICT
        return {'msg': 'A node already exists with the given name.'}


@hug.get('/{node_id}')
def get_node(node_id: str, response):
    try:
        result = NodeService.get_by_id(node_id)
        if result is None:
            response.status = hug.HTTP_NOT_FOUND
            return {'msg': 'Node not found with the given ID.'}
        return Node.Schema().dump(result)
    except InvalidId:
        response.status = hug.HTTP_BAD_REQUEST
        return {'msg': 'Invalid ID.'}


@hug.delete('/{node_id}')
def delete_node(node_id: str, response):
    result = NodeService.delete(node_id)
    if result is None:
        response.status = hug.HTTP_NOT_FOUND
        return {'msg': 'Node not found with the given ID.'}
    return Node.Schema(exclude=['_id']).dump(result)
