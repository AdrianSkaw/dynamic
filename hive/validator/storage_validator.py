from rest_framework import serializers


class StorageValidator:
    def __init__(self, entity_field_type_provider):
        self.__entity_field_type_provider = entity_field_type_provider

    @staticmethod
    def validate_request_data_names(data: dict, fields: list) -> None:
        # check if all required fields are the same
        required_fields = set([field['name'] for field in fields])
        provided_fields = set(data.keys())
        if not required_fields.issubset(provided_fields):
            missing_fields = required_fields - provided_fields
            raise serializers.ValidationError({'error': f'Missing required fields: {", ".join(missing_fields)}'})

    def validate_request_data_types(self, data: dict, fields: list) -> None:
        for field in fields:
            if field['name'] in data:
                self.__validate_field_type_exists(field)

    def __validate_field_type_exists(self, field: dict) -> None:
        if not self.__entity_field_type_provider.get(field['type']):
            raise serializers.ValidationError({'error': f'Invalid type of field {field["type"]}'})
