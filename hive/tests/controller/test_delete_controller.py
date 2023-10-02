import os
import pathlib

from django.db import connection
from django.test import TestCase
from django.urls import reverse
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.test import APIClient

from hive.di.base_container import BaseContainer
from hive.entity.entity_model import Entity
from hive.entity.entity_type_model import EntityType
from hive.repository.entity_repository import EntityRepository
from hive.service.dto.request_data import RequestData

project_dir = pathlib.Path(__file__).parent.resolve().parent.parent
env_file = project_dir / '.env'
load_dotenv(env_file)


class TestDeleteController(TestCase):

    def setUp(self):
        self.__entity_create_service = BaseContainer.create_service()
        self.__client = APIClient()
        self.__cursor = connection.cursor()
        self.__entity_create_repository = EntityRepository()
        self.__entity_type_obj = EntityType(1, 'History', 'HistoryClass')
        user_name = os.environ.get('HIVE_USER')
        password = os.environ.get('HIVE_PASS')
        payload = {
            'username': user_name,
            'password': password
        }
        self.__valid_payload = {
            "name": "test_entity_8",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": 0},
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id"],
            "type": "History"
        }
        token_res = self.__client.post(reverse('token_obtain_pair'), data=payload)
        token = token_res.data.get('access')
        self.__client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.__entity_name = self.__valid_payload['name']
        self.__entity_post_url = reverse('create-entity')
        self.__entity_delete_url = reverse('delete-entity', kwargs={'name': self.__entity_name})

    def __create_table(self, entity: Entity):
        fields = 'entity_id int NOT NULL, name varchar(10) NOT NULL, age int NOT NULL'
        identity = ','.join(entity.identity)
        table_name = "entity_" + entity.name
        query = ("CREATE TABLE {} ({} ,PRIMARY KEY ({}))").format(
            table_name, fields, identity)
        # Execute query
        self.__cursor.execute(query)

    def test_delete_entity_success(self):
        # before deleting the models, create it first
        request_data = RequestData(self.__valid_payload)
        entity = self.__entity_create_repository.create(request_data, self.__entity_type_obj)
        self.__create_table(entity)
        # then delete it
        response = self.__client.delete(self.__entity_delete_url)
        excepted_response_content = b'{"id":null,"name":"test_entity_8","fields":[{"name":"entity_id","type":"int",' \
                                    b'"config":{},"default":0,"nullable":false},{"name":"name","type":"str",' \
                                    b'"config":{"length":10},"default":"test","nullable":false},{"name":"age",' \
                                    b'"type":"int","config":{},"default":0,"nullable":false}],"identity":["entity_id"]}'
        # check if a table is deleted
        valid_payload_name = self.__valid_payload['name']
        table_name = f'hive.entity_{valid_payload_name}'
        table_list = connection.introspection.table_names()
        table_exists = table_name in table_list
        entity_exists = Entity.objects.filter(name=self.__entity_name).exists()
        self.assertFalse(table_exists)
        self.assertFalse(entity_exists)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, excepted_response_content)

    def test_delete_non_existent_entity(self):
        entity_not_existing_url = self.__entity_post_url + f'/Nonexistent Entity'
        response = self.__client.delete(entity_not_existing_url)
        excepted_response_content = b'{"detail":"Entity not exist"}'
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.content, excepted_response_content)

    def tearDown(self):
        self.__client.credentials()
        self.__cursor.close()
        super().tearDown()
