from django.db import connection
from psycopg import sql

from hive.repository.physical_table_storage_repository_interface import PhysicalTableStorageRepositoryInterface


class PhysicalTableStorageRepository(PhysicalTableStorageRepositoryInterface):

    @staticmethod
    def execute(query: str):
        with connection.cursor() as cursor:
            cursor.execute(query)

    @staticmethod
    def get_existing_columns(schema, table_name: str) -> list:
        query = sql.SQL(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = '{}' AND table_name = '{}'").format(
            sql.SQL(schema), sql.SQL(table_name))

        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = cursor.fetchall()
        return [col[0] for col in columns]

    @staticmethod
    def table_exists(schema, table_name: str) -> bool:
        query = sql.SQL("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}');").format(
            sql.SQL(schema), sql.SQL(table_name))
        with connection.cursor() as cursor:
            cursor.execute(query)
            is_found = cursor.fetchone()[0]
            return is_found

    @staticmethod
    def get_sql_type(entity_field_type: str):
        query = sql.SQL("SELECT sql_type FROM hive_entityfieldtype WHERE name = '{}';").format(sql.SQL(entity_field_type))
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()[0]
