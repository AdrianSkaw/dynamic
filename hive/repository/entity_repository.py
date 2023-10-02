from rest_framework.exceptions import NotFound

from hive.entity.entity_model import Entity
from hive.service.dto.request_data import RequestData


class EntityRepository:

    @staticmethod
    def is_exist(name: str):
        return Entity.objects.filter(name=name).exists()

    @staticmethod
    def get_by_name(name: str):
        try:
            entity = Entity.objects.get(name=name)
        except Entity.DoesNotExist:
            raise NotFound("Entity not exist")
        return entity

    @staticmethod
    def create(request_data: RequestData, entity_type_obj) -> Entity:
        entity = Entity.objects.create(
            name=request_data.name,
            fields=request_data.fields,
            identity=request_data.identity,
            primary_keys=request_data.primary_keys,
            type=entity_type_obj
        )
        return entity

    @staticmethod
    def delete(entity: Entity):
        entity.delete()
