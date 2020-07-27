import unittest

import mongomock

from unittest import mock

from bson.objectid import ObjectId

from shipyard.node.model import Node
from shipyard.node.service import NodeService


mockdb = mongomock.MongoClient().shipyard
test_nodes = Node.Schema().load([
    {
        'name': 'Test1',
        'ip': '1.1.1.1',
        'ssh_user': 'Test1',
        'ssh_pass': 'Test1'
    },
    {
        'name': 'Test2',
        'ip': '2.2.2.2',
        'ssh_user': 'Test2',
        'ssh_pass': 'Test2'
    }
], many=True)


@mock.patch('shipyard.node.service.db', mockdb)
class TestService(unittest.TestCase):

    def setUp(self):
        inserted_ids = mockdb.nodes.insert_many(
            Node.Schema(exclude=['_id']).dump(test_nodes, many=True)
        ).inserted_ids

        for i in range(len(test_nodes)):
            test_nodes[i]._id = inserted_ids[i]

    def tearDown(self):
        mockdb.nodes.delete_many({})

    def test_get_all(self):
        results = NodeService.get_all()
        self.assertEqual(len(results), len(test_nodes))

    def test_get_by_id(self):
        result = NodeService.get_by_id(test_nodes[0]._id)
        self.assertEqual(result.name, test_nodes[0].name)
        self.assertEqual(result.ip, test_nodes[0].ip)
        self.assertEqual(result.ssh_user, test_nodes[0].ssh_user)
        self.assertEqual(result.ssh_pass, test_nodes[0].ssh_pass)

        result = NodeService.get_by_id(str(ObjectId()))
        self.assertIsNone(result)

    def test_get_by_name(self):
        result = NodeService.get_by_name(test_nodes[0].name)
        self.assertEqual(result.name, test_nodes[0].name)
        self.assertEqual(result.ip, test_nodes[0].ip)
        self.assertEqual(result.ssh_user, test_nodes[0].ssh_user)
        self.assertEqual(result.ssh_pass, test_nodes[0].ssh_pass)

        result = NodeService.get_by_name('error')
        self.assertIsNone(result)

    def test_create(self):
        new_node = Node.Schema().load({
            'name': 'Test3',
            'ip': '3.3.3.3',
            'ssh_user': 'Test3',
            'ssh_pass': 'Test3'
        })

        try:
            NodeService.create(new_node)
            self.assertEqual(mockdb.nodes.count_documents({}),
                             len(test_nodes)+1)
        except ValueError:
            self.fail()

        with self.assertRaises(ValueError):
            NodeService.create(new_node)

        self.assertEqual(mockdb.nodes.count_documents({}), len(test_nodes)+1)

    def test_delete(self):
        result = NodeService.delete(test_nodes[0]._id)
        self.assertEqual(result.name, test_nodes[0].name)
        self.assertEqual(result.ip, test_nodes[0].ip)
        self.assertEqual(result.ssh_user, test_nodes[0].ssh_user)
        self.assertEqual(result.ssh_pass, test_nodes[0].ssh_pass)
        self.assertEqual(mockdb.nodes.count_documents({}), len(test_nodes)-1)

        result = NodeService.delete(str(ObjectId()))
        self.assertIsNone(result)
        self.assertEqual(mockdb.nodes.count_documents({}), len(test_nodes)-1)
