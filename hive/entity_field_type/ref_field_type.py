from hive.entity_field_type.configuration.configuration_builder import ConfigBuilder
from hive.entity_field_type.entity_field_type_interface import EntityFieldTypeInterface


class RefFieldType(EntityFieldTypeInterface):
    def __init__(self, storage_repository, entity_repository, schema):
        self.__storage_repository = storage_repository
        self.__entity_repository = entity_repository
        self.__schema = schema

    def configure(self, config: ConfigBuilder):
        config.add("storage", "str", None, False)
        config.add("field", "str", None, False)

    def valid(self, field_config: dict):
        pass

    def encode(self, value, config: dict):
        response = self.__storage_repository.find_by_keys(schema=self.__schema, table_name=config['storage'],
                                                          columns=[config['field']], keys=value)
        return response[config['field']]

    def decode(self, value, config: dict):
        columns = self.__get_columns(config['storage'])
        response = self.__storage_repository.find_by_keys(schema=self.__schema, table_name=config['storage'],
                                                          columns=columns, keys=value)
        return response

    def validate_value(self, value, config: dict):
        if not self.__entity_repository.is_exist(name=config['storage']):
            raise ValueError("Storage not exist")

    def __get_columns(self, storage: str) -> list:
        entity = self.__entity_repository.get_by_name(storage)
        columns = []
        for field in entity.fields:
            columns.append(field['name'])
        return columns
