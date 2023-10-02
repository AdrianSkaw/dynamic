import threading

from hive.di.entity_field_type_provider import EntityFieldTypeProvider
from hive.entity.entity_model import Entity
from hive.repository.storage_repository import StorageRepository
from hive.storage.storage_interface import StorageInterface
from hive.validator.storage_validator import StorageValidator


class UpdateStorage(StorageInterface):
    def __init__(self,
                 storage_validator: StorageValidator,
                 storage_repository: StorageRepository,
                 entity_field_type_provider: EntityFieldTypeProvider,
                 ):
        self.__storage_validator = storage_validator
        self.__storage_repository = storage_repository
        self.__entity_field_type_provider = entity_field_type_provider
        self.__lock = threading.RLock()

    def configure(self, entity: Entity) -> dict:
        not_null_fields = self.__get_not_null_fields(entity)
        columns = self.__get_columns(entity)
        config_dict = self.__prepare_config_dict(entity.fields)
        return {
            'identities': entity.identity,
            'not_null_fields': not_null_fields,
            'columns': columns,
            'primary_keys': entity.primary_keys,
            'config': config_dict
        }

    def consume(self, schema, name: str, data: dict, config: dict) -> dict:
        # encode and validate the data
        data = self.__data_processes(data, config)
        primary_keys = self.__get_primary_keys(data, config)
        columns = config['columns']
        # check if a record with the same identities already exists
        existing_record = self.__storage_repository.find_by_keys(columns, primary_keys, name, schema)
        # if no existing record, create a new one
        if not existing_record:
            return self.__storage_repository.create(schema=schema, table_name=name, columns=columns, data=data)

        # update the existing record
        return self.__storage_repository.update(schema=schema, table_name=name, columns=columns, data=data,
                                                identities=primary_keys)

    def is_valid(self, data: dict, fields: list) -> bool:
        self.__storage_validator.validate_request_data_types(data=data, fields=fields)
        self.__storage_validator.validate_request_data_names(data, fields)

        return True

    @staticmethod
    def __prepare_config_dict(fields: dict) -> dict:
        config_dict = {}
        for field in fields:
            config_dict[field['name']] = field['config']
            config_dict[field['name']]['type'] = field['type']
        return config_dict

    def __data_processes(self, data: dict, config: dict) -> dict:
        for key, value in data.items():
            type_ = config['config'][key]['type']
            entity_field_type = self.__entity_field_type_provider.get(type_)
            data[key] = entity_field_type.encode(value, config['config'][key])
            entity_field_type.validate_value(data[key], config['config'][key])
        return data

    @staticmethod
    def __get_primary_keys(data: dict, config: dict) -> dict:
        primary_keys = {}
        for pk in config['primary_keys']:
            if pk not in data:
                raise ValueError(f'Missing primary keys field: {pk}')
            primary_keys[pk] = data[pk]
        return primary_keys

    @staticmethod
    def __get_not_null_fields(entity: Entity) -> list:
        not_null_fields = []
        for field in entity.fields:
            if not field['nullable']:
                not_null_fields.append(field['name'])
        return not_null_fields

    @staticmethod
    def __get_columns(entity) -> list:
        columns = []
        for field in entity.fields:
            columns.append(field['name'])
        return columns
