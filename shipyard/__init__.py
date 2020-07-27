import hug

from shipyard.node import controllers as node_controllers
from shipyard.task import controllers as task_controllers

api = hug.API(__name__)
api.extend(node_controllers, '/nodes')
api.extend(task_controllers, '/tasks')
