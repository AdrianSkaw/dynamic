from hive.entity_field_type.configuration.configuration_builder import ConfigBuilder
from hive.entity_field_type.entity_field_type_interface import EntityFieldTypeInterface


class StringEntityFieldType(EntityFieldTypeInterface):

    def configure(self, config: ConfigBuilder):
        config.add("length", "int", 255)

    def valid(self, field_config: dict):
        pass

    def encode(self, value, config: dict):
        return value

    def decode(self, value, config: dict):
        return value

    def validate_value(self, value, config: dict):
        if not isinstance(value, str):
            raise ValueError("Value: {} is not a string.".format(value))
        max_length = config.get("max_length", None)
        if max_length and len(value) > max_length:
            raise ValueError("Value is too long.")
