from datetime import datetime

from rest_framework import serializers

from hive.entity_field_type.configuration.configuration_builder import ConfigBuilder
from hive.entity_field_type.entity_field_type_interface import EntityFieldTypeInterface


class DateTimeEntityFieldType(EntityFieldTypeInterface):
    # Format "Y-m-d H:i:s" in python is equal to "YYYY-MM-DD HH:MM:SS" in SQL
    FORMAT = "%Y-%m-%d %H:%M:%S"
    SQL_NOW = "CURRENT_TIMESTAMP"

    def configure(self, config: ConfigBuilder):
        pass

    def valid(self, field_config: dict):
        pass

    def encode(self, value, config: dict):
        if value is None or value == "":
            return None
        if value == self.SQL_NOW:
            return datetime.now().strftime(self.FORMAT)
        if isinstance(value, datetime):
            return value.strftime(self.FORMAT)

    def decode(self, value, config: dict):
        if isinstance(value, datetime):
            return value.strftime(self.FORMAT)
        if isinstance(value, str):
            return datetime.strptime(value, self.FORMAT)

    def validate_value(self, value, config: dict):
        if not isinstance(value, str):
            raise serializers.ValidationError("Value {} is not string.".format(value))
        try:
            datetime.strptime(value, self.FORMAT)
        except ValueError:
            raise serializers.ValidationError("Incorrect data format, should be {}".format(self.FORMAT))
