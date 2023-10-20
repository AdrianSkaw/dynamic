from typing import Dict

from django.db import connection
from psycopg import sql


class StorageRepository:

    @staticmethod
    def find_by_keys(columns: list, keys: dict, table_name: str, schema: str) -> Dict[str, str]:
        query = sql.SQL("SELECT * FROM {}.{} WHERE {}").format(
            sql.Identifier(schema),
            sql.Identifier(table_name),
            sql.SQL(" AND ".join([f"{key} = %s" for key in keys]))
        )
        with connection.cursor() as cursor:
            cursor.execute(query, tuple(keys.values()))
            row = cursor.fetchone()

        if not row:
            return {}
        return dict(zip(columns, row))

    def create(self, schema, table_name: str, columns: list, data: dict) -> Dict[str, str]:
        keys = data.keys()
        placeholders = ', '.join(['%s'] * len(data))
        query_columns = ', '.join(keys)
        values = tuple(data.values())
        query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({}) RETURNING *;").format(
            sql.Identifier(schema),
            sql.Identifier(table_name),
            sql.SQL(query_columns),
            sql.SQL(placeholders)
        )
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            row = cursor.fetchone()
        return dict(zip(columns, row))

    def update(self, schema: str, table_name: str, columns: list, data: dict, identities: dict) -> Dict[str, str]:
        set_values = ", ".join([f"{key} = %s" for key in data.keys()])
        values = tuple(data.values()) + tuple(identities.values())
        query = sql.SQL("UPDATE {}.{} SET {} WHERE {} RETURNING *;").format(
            sql.Identifier(schema),
            sql.Identifier(table_name),
            sql.SQL(set_values),
            sql.SQL(" AND ".join([f"{identity} = %s" for identity in identities]))
        )
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            row = cursor.fetchone()
            return dict(zip(columns, row))
