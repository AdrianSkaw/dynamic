from hive.entity_field_type.configuration.configuration_builder import ConfigBuilder
from hive.entity_field_type.entity_field_type_interface import EntityFieldTypeInterface


class FloatEntityFieldType(EntityFieldTypeInterface):

    def configure(self, config: ConfigBuilder):
        pass

    def valid(self, field_config: dict):
        pass

    def encode(self, value, config: dict):
        return float(value)

    def decode(self, value, config: dict):
        return value

    def validate_value(self, value, config: dict):
        if not isinstance(value, float):
            raise ValueError("Value: {} is not a float.".format(value))
