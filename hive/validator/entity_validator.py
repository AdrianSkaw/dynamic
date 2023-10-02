from rest_framework import serializers

from hive.di.entity_field_type_provider import EntityFieldTypeProvider
from hive.repository.entity_repository import EntityRepository
from hive.repository.entity_type_repository import EntityTypeRepository
from hive.service.dto.request_data import RequestData


class EntityValidator:

    def __init__(self, entity_repository: EntityRepository,
                 entity_type_repository: EntityTypeRepository,
                 entity_field_type_provider: EntityFieldTypeProvider
                 ):

        self.__entity_repository = entity_repository
        self.__entity_type_repository = entity_type_repository
        self.__entity_field_type_provider = entity_field_type_provider

    def __validate_name(self, name: str):
        if self.__entity_repository.is_exist(name):
            raise serializers.ValidationError('Entity already exists')

    def __validate_fields(self, fields: list):
        self.__validate_fields_structure(fields)
        self.__validate_fields_uniqueness(fields)
        self.__validate_fields_names(fields)
        self.__validate_fields_type(fields)
        self.__validate_fields_config(fields)

    @staticmethod
    def __validate_fields_structure(fields: list):
        required_keys = {'name', 'type', 'config', 'nullable'}
        for field in fields:
            if not isinstance(field, dict):
                raise serializers.ValidationError('Field is not a dictionary')
            if not all(key in field.keys() for key in required_keys):
                raise serializers.ValidationError('Missing field key in fields')
            if not isinstance(field['config'], dict):
                raise serializers.ValidationError('Config is not a dictionary')

    @staticmethod
    def __validate_fields_uniqueness(fields: list):
        field_names = [field['name'] for field in fields]
        if len(set(field_names)) != len(field_names):
            raise serializers.ValidationError('Column names in the "fields" field are not unique')

    @staticmethod
    def __validate_fields_names(fields: list):
        for field in fields:
            if field.get('name') == 'id':
                raise serializers.ValidationError("Invalid value - the 'name' field cannot be named 'id'")

    def __validate_fields_type(self, fields: list):
        for field in fields:
            self.__validate_field_type(field)

    def __validate_field_type(self, field: dict):
        if not isinstance(field['name'], str) or not isinstance(field['type'], str):
            raise serializers.ValidationError('Invalid type of field')
        if not self.__entity_field_type_provider.get(field['type']):
            raise serializers.ValidationError(f'Invalid value - the "type" field')

    @staticmethod
    def validate_data_type(data):
        if not isinstance(data, dict):
            raise serializers.ValidationError('Invalid type of data')
        if not isinstance(data['name'], str) or not isinstance(data['fields'], list) or not isinstance(data['identity'],
                                                                                                       list) or not isinstance(
            data['primary_keys'], list):
            raise serializers.ValidationError('Invalid type of data')

    @staticmethod
    def __validate_identity(identity: list, field_names: list):
        if not all(
                [all(isinstance(iden, str) and iden in field_names for iden in identity)]):
            raise serializers.ValidationError('Invalid structure of data in the "identity" field')

    @staticmethod
    def __validate_primary_keys(primary_keys: list, field_names: list):
        if not isinstance(primary_keys, list):
            raise serializers.ValidationError('Invalid type of data in the "primary_keys" field')
        for pk in primary_keys:
            if not isinstance(pk, str):
                raise serializers.ValidationError('Invalid type of data in the "primary_keys" field')
            if pk not in field_names:
                raise serializers.ValidationError(
                    'Invalid value - the "primary_keys" field is not in the "fields" field')

    def __validate_entity_type(self, entity_type: str):
        if not self.__entity_type_repository.get(entity_type):
            raise serializers.ValidationError('Entity type does not exist')

    def validate_request_data(self, request_data: RequestData) -> None:

        self.__validate_name(request_data.name)
        self.__validate_fields(request_data.fields)
        self.__validate_identity(request_data.identity, [field['name'] for field in request_data.fields])
        self.__validate_entity_type(request_data.entity_type)
        self.__validate_primary_keys(request_data.primary_keys, [field['name'] for field in request_data.fields])

    @staticmethod
    def validate_all_keys_exist(request_data: RequestData) -> None:
        if not all([request_data.name, request_data.fields, request_data.identity, request_data.primary_keys, ]):
            raise serializers.ValidationError('Missing field key in request data')

    def __validate_fields_config(self, fields):
        for field in fields:
            if field['type'] == 'ref':
                storage = field['config'].get('storage')
                reference_filed = field['config'].get('field')
                try:
                    entity = self.__entity_repository.get_by_name(storage)
                except:
                    raise serializers.ValidationError('Invalid value - the "storage" table not exist')
                found = False
                for entity_field in entity.fields:
                    if entity_field['name'] == reference_filed:
                        found = True
                        break
                if not found:
                    raise serializers.ValidationError(f'Invalid value - the "field" field is not exist in {storage} table')
