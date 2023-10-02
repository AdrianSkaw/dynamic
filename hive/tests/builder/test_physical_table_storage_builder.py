import pathlib

from django.db import connection
from django.test import TestCase
from dotenv import load_dotenv

from hive.builder.dto.field import Field
from hive.di.base_container import BaseContainer
from hive.di.repository_container import RepositoryContainer

project_dir = pathlib.Path(__file__).parent.resolve().parent.parent
env_file = project_dir / '.env'
load_dotenv(env_file)


class TestPhysicalTableStorageBuilder(TestCase):
    def setUp(self):
        self.__cursor = connection.cursor()
        self.__valid_payload = {
            "name": "test_entity_8",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": 0},
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id"],
            "type": "Update"
        }

        base_container = BaseContainer()
        repository_container = RepositoryContainer()
        self.__entity_create_service = base_container.create_service()
        self.__physical_table_storage_builder = base_container.physical_table_storage_builder()
        self.__physical_table_storage_repository = repository_container.physical_table_storage_repository()

    def prepare_test(self, payload):
        entity = self.__entity_create_service.create_entity(payload)
        self.__physical_table_storage_builder.set_name(entity.name)
        self.__physical_table_storage_builder.set_identity(entity.identity)
        self.__physical_table_storage_builder.set_primary_keys(entity.primary_keys)
        for field in entity.fields:
            field = Field(name=field.get('name'), type=field.get('type'), config=field.get('config'),
                          nullable=field.get('nullable'),
                          default=field.get('default'))
            self.__physical_table_storage_builder.add_field(field)
        return entity

    def test_add_field(self):
        entity = self.prepare_test(self.__valid_payload)
        field = Field(name='test_field', type='int', config={}, nullable=False, default=0)
        self.__physical_table_storage_builder.add_field(field=field)
        query = self.__physical_table_storage_builder.build()
        self.__physical_table_storage_repository.execute(query)
        excepted_columns = ['entity_id', 'name', 'age', 'test_field']
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'hive' AND table_name = '{entity.name}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = cursor.fetchall()
        columns = [col[0] for col in columns]
        self.assertEqual(excepted_columns, columns)

    def test_remove_field(self):
        entity = self.__entity_create_service.create_entity(self.__valid_payload)
        name = entity.name
        field = Field(name='age', type='int', config={}, nullable=False, default=0)
        self.__physical_table_storage_builder.set_name(name=name)
        self.__physical_table_storage_builder.remove_field(field=field)
        query = self.__physical_table_storage_builder.build()
        self.__physical_table_storage_repository.execute(query)
        excepted_columns = ['entity_id', 'name']
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'hive' AND table_name = '{name}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = cursor.fetchall()
        columns = [col[0] for col in columns]
        self.assertEqual(excepted_columns, columns)

    def test_add_table(self):

        name = "test table ;)"
        self.__physical_table_storage_builder.set_name(name)
        self.__physical_table_storage_builder.set_identity(
            ["kolumieńka", "nazwa"]
        )
        self.__physical_table_storage_builder.set_primary_keys(
            ["kolumieńka", "nazwa"]
        )
        self.__physical_table_storage_builder.add_field(
            Field(name="nazwa", type="str", config={"length": 200}, nullable=True, default="domślnie to"))
        self.__physical_table_storage_builder.add_field(
            Field(name="kolumieńka", type="str", config={"length": 200}, required=False, default="domślnie to",
                  nullable=True))
        query = self.__physical_table_storage_builder.build()
        self.__physical_table_storage_repository.execute(query)
        excepted_columns = ['nazwa', 'kolumieńka']
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'hive' AND table_name = '{name}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = cursor.fetchall()
        columns = [col[0] for col in columns]
        self.assertEqual(excepted_columns, columns)

    def test_add_and_remove_field(self):
        entity = self.prepare_test(self.__valid_payload)
        self.__physical_table_storage_builder.add_field(
            Field(name="nazwa", type="str", config={"length": 200}, nullable=True, default="domślnie to"))
        self.__physical_table_storage_builder.add_field(
            Field(name="kolumienka", type="str", config={"length": 200}, required=False, default="domślnie to",
                  nullable=True))
        removed_field = Field(name='age', type='int', config={}, nullable=False, default=0)
        self.__physical_table_storage_builder.remove_field(field=removed_field)
        query = self.__physical_table_storage_builder.build()
        self.__physical_table_storage_repository.execute(query)

        excepted_columns = ['entity_id', 'name', 'nazwa', 'kolumienka']
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'hive' AND table_name = '{entity.name}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = cursor.fetchall()
        columns = [col[0] for col in columns]
        self.assertEqual(excepted_columns, columns)

    def test_build_without_set_table_name(self):
        self.__entity_create_service.create_entity(self.__valid_payload)
        excepted_error = "[ErrorDetail(string='Name is required.', code='invalid')]"
        try:
            query = self.__physical_table_storage_builder.build()
            self.__physical_table_storage_repository.execute(query)
        except Exception as e:
            e = str(e)
            self.assertEqual(excepted_error, e)

    def test_build_without_add_fields(self):
        entity = self.__entity_create_service.create_entity(self.__valid_payload)
        self.__physical_table_storage_builder.set_name(entity.name)
        excepted_error = "[ErrorDetail(string='No changes to apply.', code='invalid')]"
        try:
            query = self.__physical_table_storage_builder.build()
            self.__physical_table_storage_repository.execute(query)
        except Exception as e:
            e = str(e)
            self.assertEqual(excepted_error, e)

    def test_build_table_without_default(self):
        name = "test table ;)"
        self.__physical_table_storage_builder.set_name(name)
        self.__physical_table_storage_builder.set_identity(
            ["kolumieńka", "nazwa"]
        )
        self.__physical_table_storage_builder.set_primary_keys(
            ["kolumieńka", "nazwa"]
        )
        self.__physical_table_storage_builder.add_field(
            Field(name="nazwa", type="str", config={"length": 200}, nullable=True))
        self.__physical_table_storage_builder.add_field(
            Field(name="kolumieńka", type="str", config={"length": 200}, required=False, nullable=True))
        query = self.__physical_table_storage_builder.build()
        self.__physical_table_storage_repository.execute(query)

        table_name = f'hive.{name}'
        excepted_columns = ['nazwa', 'kolumieńka']
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'hive' AND table_name = '{name}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = cursor.fetchall()
        columns = [col[0] for col in columns]
        self.assertEqual(excepted_columns, columns)

    def test_create_table_with_datetime(self):
        valid_payload = {
            "name": "test_entity_18",
            "fields": [
                {"name": "entity_id", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "name", "type": "str", "config": {'length': 10}, "nullable": False, "default": "test"},
                {"name": "age", "type": "int", "config": {}, "nullable": False, "default": 0},
                {"name": "datetime", "type": "date", "config": {}, "nullable": False, "default": "CURRENT_TIMESTAMP"}
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id"],
            "type": "Update"
        }
        entity = self.prepare_test(valid_payload)
        self.__physical_table_storage_builder.add_field(
            Field(name="nazwa", type="str", config={"length": 200}, nullable=True, default="domślnie to"))
        self.__physical_table_storage_builder.add_field(
            Field(name="kolumienka", type="str", config={"length": 200}, required=False, default="domślnie to",
                  nullable=True))
        removed_field = Field(name='age', type='int', config={}, nullable=False, default=0)
        self.__physical_table_storage_builder.remove_field(field=removed_field)
        query = self.__physical_table_storage_builder.build()
        self.__physical_table_storage_repository.execute(query)

        table_name = f'hive.{entity.name}'
        excepted_columns = ['entity_id', 'name', 'datetime', 'nazwa', 'kolumienka']
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'hive' AND table_name = '{entity.name}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = cursor.fetchall()
        columns = [col[0] for col in columns]
        self.assertEqual(excepted_columns, columns)

    def test_create_table_with_reference_except_success(self):
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
        query = "CREATE SCHEMA hive_2;"
        with connection.cursor() as cursor:
            cursor.execute(query)
        self.__entity_create_service.create_entity(payload_1)
        entity = self.__entity_create_service.create_entity(payload_2)

        excepted_columns = ['entity_id', 'name', 'ref_field']
        query = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'hive' AND table_name = '{entity.name}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = cursor.fetchall()
        columns = [col[0] for col in columns]
        self.assertEqual(excepted_columns, columns)

    def test_create_table_with_reference_with_not_exist_storage_table_except_error(self):
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
                {"name": "ref_field", "type": "ref", "config": {"storage": "brand_3", "field": "brand_id"},
                 "nullable": False}
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id"],
            "type": "Update"
        }
        query = "CREATE SCHEMA hive_2;"
        with connection.cursor() as cursor:
            cursor.execute(query)
        self.__entity_create_service.create_entity(payload_1)
        try:
            self.__entity_create_service.create_entity(payload_2)
        except Exception as e:
            self.assertEqual(e.args[0], 'Invalid value - the "storage" table not exist')

    def test_create_table_with_reference_with_not_exist_field_in_storage_table_except_error(self):
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
                {"name": "ref_field", "type": "ref", "config": {"storage": "brand_1", "field": "brand_name"},
                 "nullable": False}
            ],
            "identity": ["entity_id"],
            "primary_keys": ["entity_id"],
            "type": "Update"
        }
        query = "CREATE SCHEMA hive_2;"
        with connection.cursor() as cursor:
            cursor.execute(query)
        self.__entity_create_service.create_entity(payload_1)
        try:
            self.__entity_create_service.create_entity(payload_2)
        except Exception as e:
            self.assertEqual(e.args[0], 'Invalid value - the "field" field is not exist in brand_1 table')


