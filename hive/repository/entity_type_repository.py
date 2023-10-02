from rest_framework import serializers

from hive.entity.entity_type_model import EntityType


class EntityTypeRepository:

    @staticmethod
    def get(entity_type: str) -> EntityType:
        try:
            return EntityType.objects.get(name=entity_type)
        except EntityType.DoesNotExist:
            raise serializers.ValidationError('Entity type does not exist')
