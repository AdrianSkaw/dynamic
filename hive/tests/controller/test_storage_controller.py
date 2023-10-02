import json
import os
import pathlib

from django.db import connection
from django.test import TestCase
from django.urls import reverse
from dotenv import load_dotenv
from psycopg2 import sql
from rest_framework import status
from rest_framework.test import APIClient

from hive.entity.entity_model import Entity
from hive.entity.entity_type_model import EntityType
from hive.repository.entity_repository import EntityRepository
from hive.repository.storage_repository import StorageRepository
from hive.service.dto.request_data import RequestData

project_dir = pathlib.Path(__file__).parent.resolve().parent.parent
env_file = project_dir / '.env'
load_dotenv(env_file)


class TestStorageController(TestCase):

    def setUp(self):
        self.__client = APIClient()
        self.__cursor = connection.cursor()
        self.__url = reverse('create-record', args=['test_entity_9'])
        self.__entity_repository = EntityRepository()
        self.__storage_repository = StorageRepository()
        self.__entity_type_obj = EntityType(2, 'Update', 'UpdateEntityType')
        user_name = os.environ.get('HIVE_USER')
        password = os.environ.get('HIVE_PASS')
        payload = {
            'username': user_name,
            'password': password
        }
        token_res = self.__client.post(reverse('token_obtain_pair'), data=payload)
        token = token_res.data.get('access')
        self.__client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.__valid_entity_payload = {"name": "test_entity_15",
                                       "fields":
                                           [{"name": "entity_id",
                                             "type": "int",
                                             "config": {"min": -2147483648,
                                                        "max": 2147483648},
                                             "nullable": False,
                                             "default": 0},
                                            {"name": "name", "type": "str",
                                             "config": {"length": 10},
                                             "nullable": False, "default": "test"},
                                            {"name": "age", "type": "int",
                                             "config": {"min": -2147483648,
                                                        "max": 2147483648},
                                             "nullable": False, "default": 0}],
                                       "identity": ["entity_id"],
                                       "primary_keys": ["entity_id"],
                                       "type": "Update"}
        self.__name = self.__valid_entity_payload['name']
        self.__fields = self.__valid_entity_payload['fields']
        self.__identity = self.__valid_entity_payload['identity']
        self.__primary_keys = self.__valid_entity_payload['primary_keys']
        self.__url = reverse('create-record', args=[self.__valid_entity_payload['name']])
        self.__valid_record_payload = {"entity_id": 20, "name": "example", "age": 20}

    def __create_table(self, entity: Entity):
        fields = ''
        for field in entity.fields:
            if field.get('type') == 'str':
                field['type'] = 'varchar(' + str(field['config']['length']) + ')'
            if field.get('type') == 'ref':
                field['type'] = ' int REFERENCES hive.' + field['config']['storage'] + f'({field["config"]["field"]})'
            fields += field.get('name') + " " + field.get("type") + " NOT NULL,"
        fields = fields[:-1]
        primary_keys = ','.join(entity.primary_keys)
        query = sql.SQL("CREATE TABLE {}.{} ({} ,PRIMARY KEY ({}))").format(
            sql.Identifier('hive'), sql.Identifier(entity.name), sql.SQL(fields), sql.SQL(primary_keys))
        # Execute query
        self.__cursor.execute(query)

    def test_update_if_record_not_exist_success(self):
        request_data = RequestData(self.__valid_entity_payload)
        self.__entity_repository.create(request_data, self.__entity_type_obj)
        self.__create_table(
            self.__entity_repository.get_by_name(name=self.__valid_entity_payload['name']))
        response = self.__client.post(self.__url, data=json.dumps(self.__valid_record_payload),
                                      content_type='application/json')
        excepted_response_content = b'{"entity_id": 20, "name": "example", "age": 20}'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_201_CREATED)

    def test_create_record_in_table_with_too_long_string(self):
        request_data = RequestData(self.__valid_entity_payload)
        self.__entity_repository.create(request_data, self.__entity_type_obj)
        self.__create_table(
            self.__entity_repository.get_by_name(name=self.__valid_entity_payload['name']))
        payload = {"entity_id": 20, "name": "test123456789", "age": 30}
        response = self.__client.post(self.__url, data=json.dumps(payload), content_type='application/json')
        excepted_response_content = b'["Error while creating record: value too long for type character varying(10)\\n"]'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_400_BAD_REQUEST)

    def test_update_if_record_exist_success(self):
        request_data = RequestData(self.__valid_entity_payload)
        entity = self.__entity_repository.create(request_data, self.__entity_type_obj)
        self.__create_table(
            self.__entity_repository.get_by_name(name=self.__valid_entity_payload['name']))
        columns = ['entity_id', 'name', 'age']
        self.__storage_repository.create(table_name=entity.name, columns=columns,
                                         data=self.__valid_record_payload, schema='hive')
        update_payload = {"entity_id": 20, "name": "example", "age": 40}
        response = self.__client.post(self.__url, data=json.dumps(update_payload), content_type='application/json')
        excepted_response_content = b'{"entity_id": 20, "name": "example", "age": 40}'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_201_CREATED)

    def test_post_request_with_invalid_entity_name(self):
        request_data = RequestData(self.__valid_entity_payload)
        self.__entity_repository.create(request_data, self.__entity_type_obj)
        url = reverse('create-record', args=['test_entity_8'])
        response = self.__client.post(url, data=json.dumps(self.__valid_record_payload),
                                      content_type='application/json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_post_request_with_invalid_field_name(self):
        request_data = RequestData(self.__valid_entity_payload)
        self.__entity_repository.create(request_data, self.__entity_type_obj)
        response = self.__client.post(self.__url,
                                      data=json.dumps({"entity_id": 20, "names": "example_text", "age": 20}),
                                      content_type='application/json')
        excepted_response_content = b'{"error":"Missing required fields:'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_invalid_field_type(self):
        # in this case age is int but we are passing string
        request_data = RequestData(self.__valid_entity_payload)
        self.__entity_repository.create(request_data, self.__entity_type_obj)
        response = self.__client.post(self.__url,
                                      data=json.dumps({"entity_id": 20, "name": 1234, "age": "20"}),
                                      content_type='application/json')
        excepted_response_content = b'["Error while creating record: Value: 1234 is not a string."]'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_datetime(self):
        valid_entity_payload = {
            "name": "test_entity_15",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "datetime", "type": "date", "config": {}, "nullable": True, "default": "CURRENT_TIMESTAMP"}
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id", "datetime"],
            "type": "Update"
        }
        request_data = RequestData(valid_entity_payload)
        self.__entity_repository.create(request_data, self.__entity_type_obj)
        self.__create_table(
            self.__entity_repository.get_by_name(name=valid_entity_payload['name']))
        response = self.__client.post(self.__url,
                                      data=json.dumps({"entity_id": 20, "name": "example", "age": 20,
                                                       "datetime": "CURRENT_TIMESTAMP"}),
                                      content_type='application/json')
        excepted_response_content = '{"entity_id": 20, "name": "example", "age": 20, "datetime":'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_201_CREATED)

    def test_post_request_with_float(self):
        valid_entity_payload = {
            "name": "test_entity_15",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "float", "type": "float", "config": {}, "nullable": True}
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id"],
            "type": "Update"
        }
        request_data = RequestData(valid_entity_payload)
        self.__entity_repository.create(request_data, self.__entity_type_obj)
        self.__create_table(
            self.__entity_repository.get_by_name(name=valid_entity_payload['name']))
        response = self.__client.post(self.__url,
                                      data=json.dumps({"entity_id": 20, "name": "example", "age": 20,
                                                       "float": 1.2}),
                                      content_type='application/json')
        excepted_response_content = '{"entity_id": 20, "name": "example", "age": 20, "float": 1.2'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_201_CREATED)

    def test_post_request_with_ref_field(self):
        payload_1 = {
            "name": "brand_1",
            "fields": [
                {"name": "brand_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "datetime", "type": "date", "config": {}, "nullable": True, "default": "CURRENT_TIMESTAMP"},
            ],
            "identity": ["brand_id"],
            "primary_keys": ["brand_id"],
            "type": "Update"
        }
        payload_2 = {
            "name": "brand_2",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "ref_field", "type": "ref", "config": {"storage": "brand_1", "field": "brand_id"},
                 "nullable": False}
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id"],
            "type": "Update"
        }
        request_data1 = RequestData(payload_1)
        self.__entity_repository.create(request_data1, self.__entity_type_obj)
        self.__create_table(
            self.__entity_repository.get_by_name(name=payload_1['name']))

        request_data2 = RequestData(payload_2)
        self.__entity_repository.create(request_data2, self.__entity_type_obj)
        self.__create_table(
            self.__entity_repository.get_by_name(name=payload_2['name']))
        url = reverse('create-record', args=[payload_1['name']])
        self.__client.post(url,
                           data=json.dumps({"brand_id": 20, "name": "example", "age": 20,
                                            "datetime": "CURRENT_TIMESTAMP"}),
                           content_type='application/json')
        url = reverse('create-record', args=[payload_2['name']])
        response = self.__client.post(url,
                                      data=json.dumps({"entity_id": 30, "name": "example", 'ref_field': {'brand_id': 20, "name": "example" }}),
                                      content_type='application/json')
        excepted_response_content = b'{"entity_id": 30, "name": "example", "ref_field": 20}'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_201_CREATED)

    def test_post_request_with_money(self):
        valid_entity_payload = {
            "name": "test_entity_15",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "money", "type": "money", "config": {}, "nullable": True}
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id"],
            "type": "Update"
        }
        request_data = RequestData(valid_entity_payload)
        self.__entity_repository.create(request_data, self.__entity_type_obj)
        self.__create_table(
            self.__entity_repository.get_by_name(name=valid_entity_payload['name']))
        response = self.__client.post(self.__url,
                                      data=json.dumps({"entity_id": 20, "name": "example", "age": 20,
                                                       "money": '234.5'}),
                                      content_type='application/json')
        excepted_response_content = b'{"entity_id": 20, "name": "example", "age": 20, "money": "$23,450.00"}'
        self.assertContains(response, excepted_response_content, status_code=status.HTTP_201_CREATED)

    def tearDown(self):
        self.__client.credentials()
        self.__cursor.close()
        super().tearDown()

