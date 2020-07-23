import hug

from .nodes import controllers as node_controllers

hug.API(__name__).extend(node_controllers, '/nodes')
