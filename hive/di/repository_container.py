from dependency_injector import containers, providers

from hive.configuration.configuration import Configuration
from hive.repository.entity_repository import EntityRepository
from hive.repository.entity_type_repository import EntityTypeRepository
from hive.repository.physical_table_storage_repository import PhysicalTableStorageRepository
from hive.repository.storage_repository import StorageRepository


class RepositoryContainer(containers.DeclarativeContainer):
    config = providers.Singleton(
        Configuration,
    )
    entity_repository = providers.Factory(
        EntityRepository
    )

    entity_type_repository = providers.Factory(
        EntityTypeRepository
    )

    storage_repository = providers.Factory(
        StorageRepository
    )

    physical_table_storage_repository = providers.Factory(
        PhysicalTableStorageRepository
    )
