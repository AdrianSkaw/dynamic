import re
import threading

from rest_framework import serializers
from unidecode import unidecode

from hive.builder.dto.field import Field
from hive.di.entity_field_type_provider import EntityFieldTypeProvider
from hive.entity.entity_model import Entity
from hive.entity_field_type.configuration.configuration_builder import ConfigBuilder
from hive.service.dto.request_data import RequestData


class CreateService:
    def __init__(self, entity_validator, entity_type_repository, entity_repository, physical_storage_builder,
                 physical_storage_repository,
                 entity_field_type_provider: EntityFieldTypeProvider

                 ):
        self.__entity_validator = entity_validator
        self.__entity_type_repository = entity_type_repository
        self.__entity_repository = entity_repository
        self.__physical_storage_builder = physical_storage_builder
        self.__physical_storage_repository = physical_storage_repository
        self.__entity_field_type_provider = entity_field_type_provider
        self.__lock = threading.RLock()

    def create_entity(self, data):
        request_data = RequestData(data)
        self.__entity_validator.validate_all_keys_exist(request_data)
        self.__entity_validator.validate_data_type(data)
        self.__transform_fields(request_data)
        self.__update_field_config(request_data)

        with self.__lock:
            self.__entity_validator.validate_request_data(request_data)
            entity_type_obj = self.__entity_type_repository.get(request_data.entity_type)
            entity = self.__entity_repository.create(request_data, entity_type_obj)
            self.__set_physical_storage_builder_fields(entity)
            query = self.__physical_storage_builder.build()
            self.__physical_storage_repository.execute(query)
            self.__physical_storage_builder.clear_object()
            return entity

    def __update_field_config(self, request_data: RequestData):
        for field in request_data.fields:
            field["config"] = self.__prepare_config(field)

    def __set_physical_storage_builder_fields(self, entity: Entity):
        self.__set_table_name(entity.name)
        self.__set_config(entity.identity)
        self.__set_primary_keys(entity.primary_keys)
        for field in entity.fields:
            self.__add_field(field)

    def __set_table_name(self, name: str):
        self.__physical_storage_builder.set_name(name)

    def __set_primary_keys(self, primary_keys: list):
        self.__physical_storage_builder.set_primary_keys(primary_keys)

    def __set_config(self, identity: list):
        self.__physical_storage_builder.set_identity(identity)

    def __add_field(self, field: dict):
        field_obj = Field(name=field.get('name'), type=field.get('type'), config=field.get('config'),
                          nullable=field.get('nullable'),
                          default=field.get('default'))
        self.__physical_storage_builder.add_field(field_obj)

    def __transform_fields(self, request_data: RequestData):
        # Replace Polish letters to english and change to lower case. Remove spaces.
        self.__unidecode_data(request_data)
        self.__to_lowercase(request_data)
        self.__replace_spaces_with_underscores(request_data)
        self.__remove_special_characters(request_data)

    @staticmethod
    def __unidecode_data(request_data: RequestData):
        request_data.name = unidecode(request_data.name)

        for field in request_data.fields:
            field['name'] = unidecode(field['name'])

        for iden in request_data.identity:
            temp = unidecode(iden)
            request_data.identity.remove(iden)
            request_data.identity.append(temp)

        for pk in request_data.primary_keys:
            temp = unidecode(pk)
            request_data.primary_keys.remove(pk)
            request_data.primary_keys.append(temp)

    @staticmethod
    def __to_lowercase(request_data: RequestData):
        request_data.name = request_data.name.lower()

        for field in request_data.fields:
            field['name'] = field['name'].lower()
            field['type'] = field['type'].lower()
            field['config'] = {k.lower(): v.lower() if isinstance(v, str) else v for k, v in field['config'].items()}

        request_data.identity = [iden.lower() for iden in request_data.identity]
        request_data.primary_keys = [pk.lower() for pk in request_data.primary_keys]

    @staticmethod
    def __replace_spaces_with_underscores(request_data: RequestData):
        request_data.name = request_data.name.replace(" ", "_")
        for field in request_data.fields:
            field['name'] = field['name'].replace(" ", "_")

    @staticmethod
    def __prepare_input_config(field_config: dict, configs: list) -> dict:
        for config in configs:
            if config.name not in field_config and config.required and config.default is None:
                raise serializers.ValidationError('Invalid value - the "config" field is missing required fields')
            if config.name not in field_config and config.default is not None:
                field_config[config.name] = config.default
            return field_config

    def __prepare_config(self, field: dict):
        entity_field_type = self.__entity_field_type_provider.get(field['type'])

        config_builder = ConfigBuilder()
        entity_field_type.configure(config_builder)
        configs = config_builder.get()
        field_config = field.get('config', {})
        if field_config:
            field_config = self.__prepare_input_config(field_config, configs)
            entity_field_type.valid(field_config)
            return field_config
        return self.__prepare_field_config(configs)

    @staticmethod
    def __prepare_field_config(configs: list) -> dict:
        field_config = {}
        for config in configs:
            if config.default is not None:
                field_config[config.name] = config.default
        return field_config

    def __remove_special_characters(self, request_data):
        request_data.name = self.__remove_special_characters_from_string(request_data.name)
        for field in request_data.fields:
            field['name'] = self.__remove_special_characters_from_string(field['name'])
        request_data.identity = [self.__remove_special_characters_from_string(iden) for iden in request_data.identity]
        request_data.primary_keys = [self.__remove_special_characters_from_string(pk) for pk in request_data.primary_keys]

    @staticmethod
    def __remove_special_characters_from_string(name):
        return re.sub('[^A-Za-z0-9_]+', '', name)
