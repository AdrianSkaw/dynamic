from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    def configure(self, config: list):
        pass

    @abstractmethod
    def consume(self, schema: str, name: str, data: dict, config: dict):
        pass

    @abstractmethod
    def is_valid(self, data: dict, fields: list) -> bool:
        pass
