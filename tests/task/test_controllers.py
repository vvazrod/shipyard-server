import unittest

import hug

from typing import List
from unittest import mock
from io import BytesIO

from bson.objectid import ObjectId

from shipyard.errors import AlreadyPresent, NotFound
from shipyard.task import controllers
from shipyard.task.model import Task


test_tasks = Task.Schema().load([
    {
        '_id': str(ObjectId()),
        'file_id': str(ObjectId()),
        'name': 'Test1',
        'runtime': 1000,
        'deadline': 1000,
        'period': 1000
    },
    {
        '_id': str(ObjectId()),
        'file_id': str(ObjectId()),
        'name': 'Test2',
        'runtime': 1000,
        'deadline': 1000,
        'period': 1000
    }
], many=True)


class MockService():

    @staticmethod
    def get_all() -> List[Task]:
        return test_tasks

    @staticmethod
    def get_by_id(task_id: str) -> Task:
        for task in test_tasks:
            if ObjectId(task_id) == task._id:
                return task

        return None

    @staticmethod
    def get_by_name(task_name: str) -> Task:
        for task in test_tasks:
            if task_name == task.name:
                return task

        return None

    @staticmethod
    def create(new_task: Task, file_name: str, file_body: BytesIO) -> str:
        for task in test_tasks:
            if new_task.name == task.name:
                raise AlreadyPresent

        return str(ObjectId())

    @staticmethod
    def update(task_id: str, new_values: dict, file_name: str, file_body: BytesIO) -> Task:
        for task in test_tasks:
            if ObjectId(task_id) == task._id:
                return task

        raise NotFound

    @staticmethod
    def delete(task_id: str) -> Task:
        for task in test_tasks:
            if ObjectId(task_id) == task._id:
                return task

        return None


@mock.patch('shipyard.task.controllers.TaskService', MockService)
class TestControllers(unittest.TestCase):

    def test_get_task_list(self):
        response = hug.test.call('GET', controllers, '')
        self.assertEqual(response.status, hug.HTTP_OK)
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data), 2)

        response = hug.test.call('GET', controllers, '', params={
            'name': test_tasks[0].name
        })
        self.assertEqual(response.status, hug.HTTP_OK)
        self.assertIsNotNone(response.data)

        response = hug.test.call('GET', controllers, '', params={
            'name': 'Error'
        })
        self.assertEqual(response.status, hug.HTTP_NOT_FOUND)
        self.assertIsNotNone(response.data)

    def test_get_task(self):
        response = hug.test.call(
            'GET', controllers, f'{str(test_tasks[0]._id)}')
        self.assertEqual(response.status, hug.HTTP_OK)
        self.assertIsNotNone(response.data)

        response = hug.test.call('GET', controllers, f'{ObjectId()}')
        self.assertEqual(response.status, hug.HTTP_NOT_FOUND)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['error'], str)

        response = hug.test.call('GET', controllers, 'error')
        self.assertEqual(response.status, hug.HTTP_BAD_REQUEST)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['error'], str)

    def test_delete_task(self):
        response = hug.test.call(
            'DELETE', controllers, f'{str(test_tasks[0]._id)}')
        self.assertEqual(response.status, hug.HTTP_OK)
        self.assertIsNotNone(response.data)

        response = hug.test.call('DELETE', controllers, f'{ObjectId()}')
        self.assertEqual(response.status, hug.HTTP_NOT_FOUND)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['error'], str)

        response = hug.test.call('DELETE', controllers, 'error')
        self.assertEqual(response.status, hug.HTTP_BAD_REQUEST)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['error'], str)
