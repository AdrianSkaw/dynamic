import threading

from rest_framework import serializers

from hive.di.entity_field_type_provider import EntityFieldTypeProvider
from hive.di.storage_provider import StorageProvider
from hive.repository.entity_repository import EntityRepository
from hive.repository.entity_type_repository import EntityTypeRepository
from hive.repository.storage_repository import StorageRepository
from hive.validator.storage_validator import StorageValidator


class StorageService:

    def __init__(self, entity_repository: EntityRepository,
                 entity_type_repository: EntityTypeRepository,
                 entity_field_type_provider: EntityFieldTypeProvider,
                 storage_repository: StorageRepository,
                 storage_validator:
                 StorageValidator,
                 storage_provider: StorageProvider,
                 schema: str,
                 ):
        self.__entity_repository = entity_repository
        self.__entity_type_repository = entity_type_repository
        self.__storage_repository = storage_repository
        self.__storage_validator = storage_validator
        self.__entity_field_type_provider = entity_field_type_provider
        self.__storage_provider = storage_provider
        self.__schema = schema
        self.__locks = {}

    def update_entity_type(self, request, entity_name: str) -> dict:
        entity = self.__entity_repository.get_by_name(entity_name)
        storage_object = self.__storage_provider.get(entity.type.class_name)
        storage_object.is_valid(request.data, entity.fields)
        config = storage_object.configure(entity)
        lock = self.__prepare_lock(entity_name)
        try:
            with lock:
                result = storage_object.consume(schema=self.__schema, name=entity_name, data=request.data,
                                                config=config)
            if not lock.locked():
                self.__locks.pop(entity_name)
            return result
        except Exception as e:
            raise serializers.ValidationError(f"Error while creating record: {str(e)}")

    def __prepare_lock(self, entity_name):
        lock = self.__locks.get(entity_name)
        if not lock:
            lock = threading.Lock()
            self.__locks[entity_name] = lock
        return lock
