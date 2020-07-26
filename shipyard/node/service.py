from typing import List

from bson.objectid import ObjectId

from shipyard.db import db

from .model import Node


class NodeService():
    """This service contains methods for all the possible node operations."""

    @staticmethod
    def get_all() -> List[Node]:
        return Node.Schema().load(db.nodes.find(), many=True)

    @staticmethod
    def get_by_id(node_id: str) -> Node:
        result = db.nodes.find_one({'_id': ObjectId(node_id)})
        if result is None:
            return None
        return Node.Schema().load(result)

    @staticmethod
    def get_by_name(node_name: str) -> Node:
        result = db.nodes.find_one({'name': node_name})
        if result is None:
            return None
        return Node.Schema().load(result)

    @staticmethod
    def create(new_node: Node) -> str:
        result = db.nodes.find_one({'name': new_node.name})
        if result is not None:
            raise ValueError('A node already exists with the given name.')
        new_id = db.nodes.insert_one(Node.Schema(
            exclude=['_id']).dump(new_node)).inserted_id
        return str(new_id)

    @staticmethod
    def delete(node_id: str) -> Node:
        result = db.nodes.find_one_and_delete({'_id': ObjectId(node_id)})
        if result is None:
            return None
        return Node.Schema().load(result)
