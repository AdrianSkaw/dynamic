from abc import ABC, abstractmethod

from hive.builder.dto.field import Field


class StorageBuilderInterface(ABC):
    """Interface for building a storage."""

    @abstractmethod
    def set_name(self, name: str):
        pass

    @abstractmethod
    def set_identity(self, identity: list):
        pass

    @abstractmethod
    def add_field(self, field: Field):
        pass

    @abstractmethod
    def remove_field(self, field: Field) -> None:
        pass

    @abstractmethod
    def set_remove(self, remove: bool) -> None:
        pass

    def build(self):
        pass
