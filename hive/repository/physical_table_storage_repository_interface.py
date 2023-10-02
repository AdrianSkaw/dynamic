from abc import abstractmethod, ABCMeta

class PhysicalTableStorageRepositoryInterface(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def execute(query: str):
        pass

    @staticmethod
    @abstractmethod
    def get_existing_columns(schema, table_name: str) -> list:
       pass
    @staticmethod
    @abstractmethod
    def table_exists(schema, table_name: str) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def get_sql_type(entity_field_type: str):
        pass
