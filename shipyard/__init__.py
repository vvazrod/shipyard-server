"""
The server's entrypoint.
"""

import hug

from shipyard.input_formats import multipart
from shipyard.node import controllers as node_controllers
from shipyard.task import controllers as task_controllers

api = hug.API(__name__)
api.http.set_input_format("multipart/form-data", multipart)

api.extend(node_controllers, '/nodes')
api.extend(task_controllers, '/tasks')
