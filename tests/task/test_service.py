import unittest

import mongomock
import gridfs

from unittest import mock
from io import BytesIO

from bson.objectid import ObjectId
from mongomock.gridfs import enable_gridfs_integration

from shipyard.errors import AlreadyPresent
from shipyard.task.model import Task
from shipyard.task.service import TaskService


enable_gridfs_integration()
mockdb = mongomock.MongoClient().shipyard
mockfs = gridfs.GridFS(mockdb)
test_tasks = Task.Schema().load([
    {
        'name': 'Test1',
        'runtime': 1000,
        'deadline': 1000,
        'period': 1000
    },
    {
        'name': 'Test2',
        'runtime': 1000,
        'deadline': 1000,
        'period': 1000
    }
], many=True)


@mock.patch('shipyard.task.service.db', mockdb)
@mock.patch('shipyard.task.service.fs', mockfs)
class TestService(unittest.TestCase):

    def setUp(self):
        for i in range(len(test_tasks)):
            with mockfs.new_file() as file:
                test_tasks[i].file_id = file._id

        inserted_ids = mockdb.tasks.insert_many(
            Task.Schema(exclude=['_id']).dump(test_tasks, many=True)
        ).inserted_ids

        for i in range(len(test_tasks)):
            test_tasks[i]._id = inserted_ids[i]

    def tearDown(self):
        for task in test_tasks:
            mockfs.delete(task.file_id)
        mockdb.tasks.delete_many({})

    def test_get_all(self):
        results = TaskService.get_all()
        self.assertEqual(len(results), len(test_tasks))

    def test_get_by_id(self):
        result = TaskService.get_by_id(test_tasks[0]._id)
        self.assertEqual(result.name, test_tasks[0].name)
        self.assertEqual(result.runtime, test_tasks[0].runtime)
        self.assertEqual(result.deadline, test_tasks[0].deadline)
        self.assertEqual(result.period, test_tasks[0].period)

        result = TaskService.get_by_id(str(ObjectId()))
        self.assertIsNone(result)

    def test_get_by_name(self):
        result = TaskService.get_by_name(test_tasks[0].name)
        self.assertEqual(result.name, test_tasks[0].name)
        self.assertEqual(result.runtime, test_tasks[0].runtime)
        self.assertEqual(result.deadline, test_tasks[0].deadline)
        self.assertEqual(result.period, test_tasks[0].period)

        result = TaskService.get_by_name('error')
        self.assertIsNone(result)

    def test_create(self):
        new_task = Task.Schema().load({
            'name': 'Test',
            'runtime': 1000,
            'deadline': 1000,
            'period': 1000
        })

        try:
            result = TaskService.create(
                new_task, 'test_file.tar.gz', BytesIO())
            self.assertEqual(mockdb.tasks.count_documents({}),
                             len(test_tasks)+1)
            self.assertIsInstance(result, str)
        except:
            self.fail()

        with self.assertRaises(AlreadyPresent):
            TaskService.create(new_task, 'test_file.tar.gz', BytesIO())

    def test_delete(self):
        result = TaskService.delete(test_tasks[0]._id)
        self.assertEqual(result.name, test_tasks[0].name)
        self.assertEqual(result.runtime, test_tasks[0].runtime)
        self.assertEqual(result.deadline, test_tasks[0].deadline)
        self.assertEqual(result.period, test_tasks[0].period)
        self.assertEqual(mockdb.tasks.count_documents({}), len(test_tasks)-1)

        result = TaskService.delete(str(ObjectId()))
        self.assertIsNone(result)
        self.assertEqual(mockdb.tasks.count_documents({}), len(test_tasks)-1)
