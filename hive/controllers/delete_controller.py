from dependency_injector.wiring import Provide
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hive.di.base_container import BaseContainer
from hive.di.repository_container import RepositoryContainer
from hive.repository.entity_repository import EntityRepository
from hive.service.delete_service import DeleteService


class DeleteController(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self,
                 entity_repository: EntityRepository = Provide[RepositoryContainer.entity_repository],
                 delete_service: DeleteService = Provide[BaseContainer.delete_service]
                 ):
        super().__init__()
        self.__entity_repository = entity_repository
        self.__delete_service = delete_service

    def delete(self, request, name: str) -> Response:
        entity = self.__entity_repository.get_by_name(name)
        self.__delete_service.delete_entity(entity)

        return Response({
            'id': entity.id,
            'name': entity.name,
            'fields': entity.fields,
            'identity': entity.identity
        },
            status=status.HTTP_200_OK)
