from psycopg2 import sql
from rest_framework import serializers

from hive.builder.dto.field import Field
from hive.builder.storage_builder_interface import StorageBuilderInterface
from hive.repository.entity_repository import EntityRepository
from hive.repository.physical_table_storage_repository import PhysicalTableStorageRepository
from hive.validator.physical_table_storage_validator import PhysicalTableStorageValidator


class PhysicalTableStorageBuilder(StorageBuilderInterface):
    """Builds a physical table storage."""

    def __init__(self,
                 physical_table_storage_repository:
                 PhysicalTableStorageRepository,
                 physical_table_storage_validator:
                 PhysicalTableStorageValidator,
                 schema: str,
                 entity_repository: EntityRepository
                 ):
        self.__name = None
        self.__identity = None
        self.__primary_keys = None
        self.__fields = []
        self.__remove_fields = []
        self.__remove = False
        self.__query = sql.SQL('')
        self.__physical_table_storage_repository: \
            PhysicalTableStorageRepository = physical_table_storage_repository
        self.__physical_table_storage_validator = physical_table_storage_validator
        self.__entity_repository = entity_repository
        self.__schema = schema

    def clear_object(self):
        self.__name = None
        self.__identity = None
        self.__primary_keys = None
        self.__fields = []
        self.__remove_fields = []
        self.__remove = False
        self.__query = sql.SQL('')

    def set_name(self, name: str):
        self.__name = name

    def set_identity(self, identity: list):
        self.__identity = identity

    def set_primary_keys(self, primary_keys: list):
        self.__primary_keys = primary_keys

    def add_field(self, field: Field):
        self.__fields.append(field)

    def remove_field(self, field: Field) -> None:
        self.__remove_fields.append(field)

    def set_remove(self, remove: bool) -> None:
        self.__remove = remove

    def build(self) -> sql.SQL:
        self.__physical_table_storage_validator.validate_name(self.__name)

        if self.__remove:
            self.__drop_table()
            return self.__query + sql.SQL(";")
        if not self.__physical_table_storage_repository.table_exists(self.__schema, self.__name):
            self.__create_table()
            return self.__query + sql.SQL(";")

        self.__query = sql.SQL('ALTER TABLE') + sql.Identifier(self.__schema) + sql.SQL(".") + sql.Identifier(
            self.__name)

        existing_columns = self.__physical_table_storage_repository.get_existing_columns(schema=self.__schema,
                                                                                         table_name=self.__name)
        drop_columns = [self.__drop_column(field) for field in self.__remove_fields if field.name in existing_columns]
        add_columns = [self.__create_column(field) for field in self.__fields if field.name not in existing_columns]

        if add_columns:
            self.__modify_columns(add_columns, "ADD")
        if drop_columns:
            self.__add_comma_if_columns_exist(add_columns)
            self.__modify_columns(drop_columns, "DROP")
        if add_columns or drop_columns:
            return self.__query + sql.SQL(";")
        raise serializers.ValidationError("No changes to apply.")

    def __add_comma_if_columns_exist(self, add_columns):
        if add_columns:
            self.__query += sql.SQL(",")

    def __modify_columns(self, columns: list, add_or_drop: str,
                         ):
        for i, column in enumerate(columns):
            self.__query += sql.SQL(f"{add_or_drop} COLUMN") + column
            if i < len(columns) - 1:
                self.__query += sql.SQL(",")

    @staticmethod
    def __drop_column(field: Field) -> sql.Identifier:
        column = sql.Identifier(field.name)
        return column

    def __drop_table(self):
        self.__query = sql.SQL("DROP TABLE IF EXISTS {}.{}").format(sql.SQL(self.__schema), sql.Identifier(self.__name))

    def __create_table(self):
        columns = [self.__create_column(field) for field in self.__fields]
        fields_sql = sql.SQL(", ").join(columns)
        identity_sql = sql.SQL(", ").join([sql.Identifier(col) for col in self.__identity])
        primary_keys_sql = sql.SQL(", ").join([sql.Identifier(col) for col in self.__primary_keys])
        table_name_sql = sql.Identifier(self.__name)
        schema_name_sql = sql.Identifier(self.__schema)
        self.__query = sql.SQL("CREATE TABLE {}.{} ({} ,PRIMARY KEY ({}), UNIQUE ({}))").format(
            schema_name_sql, table_name_sql, fields_sql, primary_keys_sql, identity_sql)

    def __create_column(self, field: Field) -> sql.Composed:
        not_null = sql.SQL("NOT NULL") if not field.nullable else sql.SQL(" ")
        default = self.__prepare_default(field)
        field.type = self.__prepare_text_field(field) if field.type == 'str' else field.type #TODO
        field.type = self.__prepare_reference_field(field) if field.type == 'ref' else field.type #TODO
        field.type = 'int' if field.type == 'money' else field.type #TODO
        column = sql.Identifier(field.name) + sql.SQL(" ") + sql.SQL(field.type) \
                 + sql.SQL(" ") + not_null + sql.SQL(" ") + default
        return column

    def __prepare_default(self, field: Field):
        if field.default:
            return self.__create_default_expression(field.type, field.default)
        return sql.SQL(" ")

    @staticmethod
    def __prepare_text_field(field: Field) -> str:
        length = field.config['length']
        return f"varchar({length})" if length < 4096 else "text"

    def __prepare_reference_field(self, field: Field) -> str:
        storage = field.config['storage']
        reference_field = field.config['field']
        entity = self.__entity_repository.get_by_name(storage)
        sql_type = self.__get_reference_type(entity, reference_field)
        return "{sql} REFERENCES {schema}.{storage}({reference_field})".format(sql=sql_type, schema=self.__schema,
                                                                               storage=storage,
                                                                               reference_field=reference_field)
    @staticmethod
    def __get_reference_type(entity, reference_field):
        for field in entity.fields:
            if field['name'] == reference_field:
                return field['type']
    @staticmethod
    def __create_default_expression(field_type: str, default_value: str) -> sql.SQL:
        if field_type == "str":
            default_value = f"'{default_value}'"
        return sql.SQL(f"DEFAULT {default_value}")
