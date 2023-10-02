from dependency_injector import containers, providers

from hive.builder.physical_table_storage_builder import PhysicalTableStorageBuilder
from hive.di.entity_field_type_provider import EntityFieldTypeProvider
from hive.di.repository_container import RepositoryContainer
from hive.di.storage_provider import StorageProvider
from hive.entity_field_type.datatime_entity_field_type import DateTimeEntityFieldType
from hive.entity_field_type.float_entity_field_type import FloatEntityFieldType
from hive.entity_field_type.int_entity_field_type import IntEntityFieldType
from hive.entity_field_type.money_field_type import MoneyFieldType
from hive.entity_field_type.ref_field_type import RefFieldType
from hive.entity_field_type.string_entity_field_type import StringEntityFieldType
from hive.service.create_service import CreateService
from hive.service.delete_service import DeleteService
from hive.service.storage_service import StorageService
from hive.storage.update_storage import UpdateStorage
from hive.validator.entity_validator import EntityValidator
from hive.validator.physical_table_storage_validator import PhysicalTableStorageValidator
from hive.validator.storage_validator import StorageValidator


class BaseContainer(containers.DeclarativeContainer):
    repository = providers.Container(
        RepositoryContainer,
    )
    config = repository.config

    int_entity_field_type = providers.Singleton(IntEntityFieldType)
    string_entity_field_type = providers.Singleton(StringEntityFieldType)
    datetime_entity_field_type = providers.Singleton(DateTimeEntityFieldType)
    float_entity_field_type = providers.Singleton(FloatEntityFieldType)
    ref_field_type = providers.Singleton(RefFieldType,
                                         storage_repository=repository.storage_repository,
                                         entity_repository=repository.entity_repository,
                                         schema=config().get_schema()
                                         )
    money_field_type = providers.Singleton(MoneyFieldType)
    entity_field_type_provider = providers.Singleton(EntityFieldTypeProvider,
                                                     int_entity_field_type=int_entity_field_type
                                                     , string_entity_field_type=string_entity_field_type
                                                     , datetime_entity_field_type=datetime_entity_field_type
                                                     , float_entity_field_type=float_entity_field_type
                                                     , ref_field_type=ref_field_type
                                                     , money_field_type=money_field_type
                                                     )

    storage_validator = providers.Factory(
        StorageValidator,
        entity_field_type_provider=entity_field_type_provider
    )

    update_storage = providers.Factory(UpdateStorage,
                                       storage_validator=storage_validator,
                                       storage_repository=repository.storage_repository,
                                       entity_field_type_provider=entity_field_type_provider,

                                       )

    storage_provider = providers.Singleton(StorageProvider,
                                           update_storage=update_storage)

    entity_validator = providers.Factory(
        EntityValidator,
        entity_repository=repository.entity_repository,
        entity_type_repository=repository.entity_type_repository,
        entity_field_type_provider=entity_field_type_provider
    )
    physical_table_storage_validator = providers.Factory(
        PhysicalTableStorageValidator
    )

    physical_table_storage_builder = providers.Singleton(
        PhysicalTableStorageBuilder,
        physical_table_storage_repository=repository.physical_table_storage_repository,
        physical_table_storage_validator=physical_table_storage_validator,
        schema=config().get_schema(),
        entity_repository=repository.entity_repository,
    )

    create_service = providers.Singleton(
        CreateService,
        entity_repository=repository.entity_repository,
        entity_type_repository=repository.entity_type_repository,
        entity_validator=entity_validator,
        physical_storage_builder=physical_table_storage_builder,
        physical_storage_repository=repository.physical_table_storage_repository,
        entity_field_type_provider=entity_field_type_provider
    )

    storage_service = providers.Singleton(
        StorageService,
        entity_repository=repository.entity_repository,
        entity_type_repository=repository.entity_type_repository,
        storage_repository=repository.storage_repository,
        storage_validator=storage_validator,
        schema=config().get_schema(),
        entity_field_type_provider=entity_field_type_provider,
        storage_provider=storage_provider
    )

    delete_service = providers.Factory(
        DeleteService,
        entity_repository=repository.entity_repository,
        physical_table_storage_repository=repository.physical_table_storage_repository,
        physical_table_storage_builder=physical_table_storage_builder
    )
