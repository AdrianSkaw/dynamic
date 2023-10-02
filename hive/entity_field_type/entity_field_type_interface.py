from abc import abstractmethod, ABCMeta

from hive.entity_field_type.configuration.configuration_builder import ConfigBuilder


class EntityFieldTypeInterface(metaclass=ABCMeta):
    @abstractmethod
    def configure(self, config: ConfigBuilder):
        pass

    @abstractmethod
    def valid(self, field_config: dict):
        pass

    @abstractmethod
    def encode(self, value, config: dict):
        pass

    @abstractmethod
    def decode(self, value, config: dict):
        pass

    @abstractmethod
    def validate_value(self, value, config: dict):
        pass
