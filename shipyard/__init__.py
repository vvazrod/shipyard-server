import hug

from shipyard.node import controllers as node_controllers

hug.API(__name__).extend(node_controllers, '/nodes')
