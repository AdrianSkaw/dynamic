from dependency_injector.wiring import Provide
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hive.di.base_container import BaseContainer
from hive.service.create_service import CreateService


class CreateController(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self,
                 entity_create_service: CreateService = Provide[BaseContainer.create_service]
                 ):
        super().__init__()
        self.__create_service = entity_create_service

    def post(self, request) -> Response:
        entity = self.__create_service.create_entity(request.data)
        return Response({
            'id': entity.id,
            'name': entity.name,
            'fields': entity.fields,
            'identity': entity.identity,
            'primary_keys': entity.primary_keys,
            'type': entity.type.name
        }, status=status.HTTP_201_CREATED)
