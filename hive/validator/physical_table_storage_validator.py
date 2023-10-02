from rest_framework import serializers


class PhysicalTableStorageValidator:

    @staticmethod
    def validate_name(name: str):
        if not name:
            raise serializers.ValidationError("Name is required.")
