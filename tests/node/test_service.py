import unittest

import mongomock
import gridfs

from unittest import mock
from typing import List

from bson.objectid import ObjectId
from mongomock.gridfs import enable_gridfs_integration

from shipyard.errors import NotFound, NotFeasible, MissingDevices, AlreadyPresent
from shipyard.node.model import Node
from shipyard.node.service import NodeService
from shipyard.task.model import Task


enable_gridfs_integration()
mockdb = mongomock.MongoClient().shipyard
mockfs = gridfs.GridFS(mockdb)
test_nodes = Node.Schema().load([
    {
        'name': 'Test1',
        'ip': '1.1.1.1',
        'ssh_user': 'Test1',
        'cpu_cores': 4,
        'tasks': [],
        'devices': [
            '/dev/test1',
            '/dev/test2'
        ]
    },
    {
        'name': 'Test2',
        'ip': '2.2.2.2',
        'ssh_user': 'Test2',
        'cpu_cores': 1
    }
], many=True)
test_tasks = Task.Schema().load([
    {
        'name': 'Test1',
        'runtime': 1000,
        'deadline': 1000,
        'period': 1000,
        'devices': [
            '/dev/test1'
        ]
    },
    {
        'name': 'Test2',
        'runtime': 1000,
        'deadline': 1000,
        'period': 1000,
        'devices': [
            '/dev/test1',
            '/dev/test3'
        ]
    },
    {
        'name': 'Test3',
        'runtime': 1000,
        'deadline': 1000,
        'period': 1000,
        'devices': [
            '/dev/test1'
        ]
    }
], many=True)


def mock_check_feasibility(tasks: List[Task], cpu_cores: int) -> bool:
    if tasks[-1].name == 'Test1':
        return True
    return False


def mock_set_up_node(address: str, ssh_user: str, ssh_pass: str):
    return


def mock_deploy_task(task_file, task: Task, node: Node):
    return


def mock_remove_task(task_name: str, node: Node):
    return


@mock.patch('shipyard.node.service.db', mockdb)
@mock.patch('shipyard.node.service.fs', mockfs)
@mock.patch('shipyard.node.service.check_feasibility', mock_check_feasibility)
@mock.patch('shipyard.node.service.set_up_node', mock_set_up_node)
@mock.patch('shipyard.node.service.deploy_task', mock_deploy_task)
@mock.patch('shipyard.node.service.remove_task', mock_remove_task)
class TestService(unittest.TestCase):

    def setUp(self):
        inserted_ids = mockdb.nodes.insert_many(
            Node.Schema(exclude=['_id']).dump(test_nodes, many=True)
        ).inserted_ids

        for i in range(len(test_nodes)):
            test_nodes[i]._id = inserted_ids[i]

        for i in range(len(test_tasks)):
            with mockfs.new_file() as file:
                test_tasks[i].file_id = file._id

        inserted_ids = mockdb.tasks.insert_many(
            Task.Schema(exclude=['_id']).dump(test_tasks, many=True)
        ).inserted_ids

        for i in range(len(test_tasks)):
            test_tasks[i]._id = inserted_ids[i]

        test_nodes[1].tasks.append(test_tasks[0])

    def tearDown(self):
        mockdb.nodes.delete_many({})

        for task in test_tasks:
            mockfs.delete(task.file_id)
        mockdb.tasks.delete_many({})

    def test_get_all(self):
        results = NodeService.get_all()
        self.assertEqual(len(results), len(test_nodes))

    def test_get_by_id(self):
        result = NodeService.get_by_id(test_nodes[0]._id)
        self.assertEqual(result.name, test_nodes[0].name)
        self.assertEqual(result.ip, test_nodes[0].ip)
        self.assertEqual(result.ssh_user, test_nodes[0].ssh_user)

        with self.assertRaises(NotFound):
            result = NodeService.get_by_id(str(ObjectId()))

    def test_get_by_name(self):
        result = NodeService.get_by_name(test_nodes[0].name)
        self.assertEqual(result.name, test_nodes[0].name)
        self.assertEqual(result.ip, test_nodes[0].ip)
        self.assertEqual(result.ssh_user, test_nodes[0].ssh_user)

        with self.assertRaises(NotFound):
            result = NodeService.get_by_name('error')

    def test_create(self):
        new_node = Node.Schema().load({
            'name': 'Test3',
            'ip': '3.3.3.3',
            'cpu_cores': 4
        })

        try:
            result = NodeService.create(new_node, 'test', 'test')
            self.assertEqual(mockdb.nodes.count_documents({}),
                             len(test_nodes)+1)
            self.assertIsInstance(result, str)
        except:
            self.fail()

        with self.assertRaises(AlreadyPresent):
            NodeService.create(new_node, 'test', 'test')
        self.assertEqual(mockdb.nodes.count_documents({}), len(test_nodes)+1)

    def test_update(self):
        result = NodeService.update(test_nodes[0]._id, {'name': 'Updated'})
        self.assertNotEqual(result.name, test_nodes[0].name)
        self.assertEqual(result.name, 'Updated')
        self.assertEqual(result.ip, test_nodes[0].ip)
        self.assertEqual(result.ssh_user, test_nodes[0].ssh_user)
        self.assertEqual(result.devices, test_nodes[0].devices)

        with self.assertRaises(NotFound):
            NodeService.update(str(ObjectId()), {})

    def test_delete(self):
        result = NodeService.delete(test_nodes[0]._id)
        self.assertEqual(result.name, test_nodes[0].name)
        self.assertEqual(result.ip, test_nodes[0].ip)
        self.assertEqual(result.ssh_user, test_nodes[0].ssh_user)
        self.assertEqual(mockdb.nodes.count_documents({}), len(test_nodes)-1)

        with self.assertRaises(NotFound):
            result = NodeService.delete(str(ObjectId()))
        self.assertEqual(mockdb.nodes.count_documents({}), len(test_nodes)-1)

    def test_add_task(self):
        try:
            result = NodeService.add_task(test_nodes[0]._id, test_tasks[0]._id)
            self.assertEqual(len(result.tasks), len(test_nodes[0].tasks)+1)
        except:
            self.fail()

        with self.assertRaises(NotFound):
            NodeService.add_task(str(ObjectId()), test_tasks[0]._id)

        with self.assertRaises(NotFound):
            NodeService.add_task(test_tasks[0]._id, str(ObjectId()))

        with self.assertRaises(MissingDevices):
            NodeService.add_task(test_nodes[0]._id, test_tasks[1]._id)

        with self.assertRaises(NotFeasible):
            NodeService.add_task(test_nodes[0]._id, test_tasks[2]._id)

    def test_remove_task(self):
        try:
            result = NodeService.remove_task(
                test_nodes[1]._id, test_tasks[0]._id)
            self.assertEqual(len(result.tasks), len(test_nodes[1].tasks)-1)
        except:
            self.fail()

        with self.assertRaises(NotFound):
            NodeService.remove_task(str(ObjectId()), test_tasks[0]._id)

        with self.assertRaises(NotFound):
            NodeService.remove_task(test_nodes[1]._id, str(ObjectId()))
