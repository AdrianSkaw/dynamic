from rest_framework import serializers

from hive.entity_field_type.configuration.configuration_builder import ConfigBuilder
from hive.entity_field_type.entity_field_type_interface import EntityFieldTypeInterface
from hive.service.money_parser import MoneyParser


class MoneyFieldType(EntityFieldTypeInterface):

    def configure(self, config: ConfigBuilder):
        config.add("min", "int", -2147483648, False)
        config.add("max", "int", 2147483648, False)

    def valid(self, field_config: dict):
        pass

    def encode(self, value, config: dict):
        money_parser = MoneyParser()
        return money_parser.convert(value, append_penny=True)

    def decode(self, value, config: dict):
        return value

    def validate_value(self, value, config: dict):
        if not isinstance(value, int):
            raise serializers.ValidationError("Value: {} is not an integer.".format(value))
        min_value = config.get("min", -2147483648)
        max_value = config.get("max", 2147483648)
        if value < min_value or value > max_value:
            raise serializers.ValidationError("Value is out of range.")
