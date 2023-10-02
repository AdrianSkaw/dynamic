import json
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


class TestCreateController(TestCase):

    def setUp(self):
        from dotenv import load_dotenv
        load_dotenv('.env')
        self.__entity_create_service = BaseContainer.create_service()
        self.__client = APIClient()
        self.__cursor = connection.cursor()
        self.__url = reverse('create-entity')
        self.__entity_create_repository = EntityRepository()
        self.__entity_type_obj = EntityType(2, 'Update', 'UpdateClass')

        user_name = os.getenv('HIVE_USER')
        password = os.getenv('HIVE_PASS')
        payload = {
            'username': user_name,
            'password': password
        }

        token_res = self.__client.post(reverse('token_obtain_pair'), data=payload)
        token = token_res.data.get('access')
        self.__client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.__valid_payload = {
            "name": "test_entity_8",
            "fields": [
                {
                    "name": "entity_id",
                    "type": "int",
                    "config": {

                    },
                    "nullable": False,
                    "default": 0
                },
                {
                    "name": "name",
                    "type": "str",
                    "config": {
                        "length": 10
                    },
                    "nullable": False,
                    "default": "test"
                },
                {
                    "name": "age",
                    "type": "int",
                    "config": {

                    },
                    "nullable": False,
                    "default": 0
                }
            ],
            "identity": [
                "entity_id"
            ],
            "primary_keys": [
                "entity_id"
            ],
            "type": "Update"
        }
        self.__name = self.__valid_payload['name']
        self.__fields = self.__valid_payload['fields']
        self.__identity = self.__valid_payload['identity']
        self.__primary_keys = self.__valid_payload['primary_keys']

    def test_create_entity_success(self):
        data = json.dumps(self.__valid_payload)
        response = self.__client.post(self.__url, data=data, content_type='application/json')
        valid_payload_name = self.__valid_payload['name']

        query = f"SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_schema = 'hive' AND table_name = '{valid_payload_name}')"
        with connection.cursor() as cursor:
            cursor.execute(query)
            table_exists = cursor.fetchone()[0]

        entity = Entity.objects.get(name=self.__valid_payload['name'])
        entity_name = entity.name
        valid_payload_name = self.__valid_payload['name']
        excepted_response = '"name":"test_entity_8","fields":[{"name":"entity_id","type":"int",' \
                            '"config":{"min":-2147483648,"max":2147483648},"nullable":false,"default":0},' \
                            '{"name":"name","type":"str","config":{"length":10},"nullable":false,"default":"test"},' \
                            '{"name":"age","type":"int","config":{"min":-2147483648,"max":2147483648},' \
                            '"nullable":false,"default":0}],"identity":["entity_id"],"primary_keys":["entity_id"],"type":"Update"}'
        self.assertEqual(entity_name, valid_payload_name)
        self.assertContains(response, excepted_response, status_code=status.HTTP_201_CREATED)
        self.assertTrue(table_exists)

    def test_create_entity_with_invalid_payload_missing_fields(self):
        invalid_payload_missing_fields = {
            "name": "test_entity",
            "identity": ["id_"],
            "primary_keys": ["entity_id"],
            'type': "History"
        }
        data = json.dumps(invalid_payload_missing_fields)
        response = self.__client.post(self.__url, data=data, content_type='application/json')
        excepted_response_content = b'["Missing field key in request data"]'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, excepted_response_content)

    def test_create_entity_without_default(self):
        valid_payload = {
            "name": "test_entity_8",
            "fields": [
                {
                    "name": "entity_id",
                    "type": "int",
                    "config": {

                    },
                    "nullable": False,
                    "default": 0
                },
                {
                    "name": "name",
                    "type": "str",
                    "config": {
                        "length": 10
                    },
                    "nullable": False,

                },
                {
                    "name": "age",
                    "type": "int",
                    "config": {

                    },
                    "nullable": False,
                }
            ],
            "identity": [
                "entity_id"
            ],
            "primary_keys": [
                "entity_id"
            ],
            "type": "Update"
        }
        data = json.dumps(valid_payload)
        response = self.__client.post(self.__url, data=data, content_type='application/json')
        excepted_response_content = '"name":"test_entity_8","fields":[{"name":"entity_id","type":"int",' \
                                    '"config":{"min":-2147483648,"max":2147483648},"nullable":false,' \
                                    '"default":0},{"name":"name","type":"str","config":{"length":10},' \
                                    '"nullable":false},{"name":"age","type":"int","config":{"min":-2147483648,' \
                                    '"max":2147483648},"nullable":false}],"identity":["entity_id"],' \
                                    '"primary_keys":["entity_id"],"type":"Update"}'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_201_CREATED)

    def test_create_entity_with_invalid_payload_wrong_identity_type(self):
        invalid_payload_wrong_identity_type = {
            "name": "test_entity_1",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": "test"},
            ],
            "identity": "entity_id",
            "primary_keys": ["entity_id"],
            "type": "History"
        }
        data = json.dumps(invalid_payload_wrong_identity_type)
        response = self.__client.post(self.__url, data=data,
                                      content_type='application/json')
        excepted_response_content = b'["Invalid type of data"]'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, excepted_response_content)

    def test_create_entity_with_invalid_payload_wrong_identity_value(self):
        invalid_payload_wrong_identity_value = {
            "name": "test_entity_1",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": "test"},
            ],
            "identity": ["wrong_id"],
            "primary_keys": ["entity_id"],
            "type": "History"
        }
        data = json.dumps(invalid_payload_wrong_identity_value)
        response = self.__client.post(self.__url,
                                      data=data,
                                      content_type='application/json')
        excepted_response_content = b'["Invalid structure of data in the \\"identity\\" field"]'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, excepted_response_content)

    def test_create_entity_with_spaces_upper_cases_special_character_and_polish_char(self):
        invalid_payload = {
            "name": "test Entity 15",
            "fields": [
                {"name": "entity_ładna?", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name 1", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age 1", "type": "int", "config": {}, "nullable": False, "default": 0},
            ],
            "identity": ["entity_ładna?"],
            "primary_keys": ["entity_ładna?"],
            "type": "Update"
        }
        data = json.dumps(invalid_payload)
        response = self.__client.post(self.__url, data=data, content_type='application/json')
        excepted_response_content = '"name":"test_entity_15","fields":[{"name":"entity_ladna","type":"int",' \
                                    '"config":{"min":-2147483648,"max":2147483648},"nullable":false,"default":0},' \
                                    '{"name":"name_1","type":"str","config":{"length":10},"nullable":false,' \
                                    '"default":"test"},{"name":"age_1","type":"int","config":{"min":-2147483648,' \
                                    '"max":2147483648},"nullable":false,"default":0}],"identity":["entity_ladna"],' \
                                    '"primary_keys":["entity_ladna"],"type":"Update"}'

        self.assertContains(response, excepted_response_content, status_code=status.HTTP_201_CREATED)

    def test_create_entity_with_invalid_payload_existing_entity(self):
        # Add a table to the database first to simulate an existing models
        request_data = RequestData(self.__valid_payload)
        self.__entity_create_repository.create(request_data, self.__entity_type_obj)
        # Add the same table again to test the error
        data = json.dumps(self.__valid_payload)
        response = self.__client.post(self.__url, data=data, content_type='application/json')
        excepted_response_content = b'["Entity already exists"]'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, excepted_response_content)

    def test_check_type_is_in_entity_type(self):
        valid_payload = {
            "name": "test_entity_1",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": "test"},
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id"],
            "type": 'Nonexistent Type'
        }
        data = json.dumps(valid_payload)
        response = self.__client.post(self.__url, data=data, content_type='application/json')
        excepted_response_content = b'["Entity type does not exist"]'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, excepted_response_content)

    def test_create_entity_with_not_exist_primary_keys(self):
        valid_payload = {
            "name": "test_entity_1",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": "test"},
            ],
            "identity": ["entity_id"],
            "primary_keys": ["not_exist_primary_keys"],
            "type": 'Update'
        }
        data = json.dumps(valid_payload)
        response = self.__client.post(self.__url, data=data, content_type='application/json')
        excepted_response_content = b'["Invalid value - the \\"primary_keys\\" field is not in the \\"fields\\" field"]'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_400_BAD_REQUEST)

    def test_create_entity_with_not_valid_type_of_primary_keys(self):
        valid_payload = {
            "name": "test_entity_1",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": "test"},
            ],
            "identity": ["entity_id"],
            "primary_keys": "not_exist_primary_keys",
            "type": 'Update'
        }
        data = json.dumps(valid_payload)
        response = self.__client.post(self.__url, data=data, content_type='application/json')
        excepted_response_content = b'["Invalid type of data"]'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        self.__client.credentials()
        self.__cursor.close()
        super().tearDown()
