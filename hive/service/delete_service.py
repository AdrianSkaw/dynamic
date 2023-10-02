from hive.repository.entity_repository import EntityRepository
from hive.repository.physical_table_storage_repository import PhysicalTableStorageRepository


class DeleteService:
    def __init__(self,
                 entity_repository: EntityRepository,
                 physical_table_storage_builder,
                 physical_table_storage_repository: PhysicalTableStorageRepository
                 ):
        super().__init__()
        self.__entity_repository = entity_repository
        self.__physical_table_storage_builder = physical_table_storage_builder
        self.__physical_table_storage_repository = physical_table_storage_repository

    def delete_entity(self, entity):
        self.__entity_repository.delete(entity)
        self.__physical_table_storage_builder.set_name(entity.name)
        self.__physical_table_storage_builder.set_remove(True)
        query = self.__physical_table_storage_builder.build()
        self.__physical_table_storage_repository.execute(query)
