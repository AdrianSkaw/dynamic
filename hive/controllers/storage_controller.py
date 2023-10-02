from dependency_injector.wiring import Provide
from django.http import JsonResponse
from rest_framework.views import APIView

from hive.di.base_container import BaseContainer
from hive.service.storage_service import StorageService


class StorageController(APIView):
    def __init__(self,
                 storage_service: StorageService = Provide[BaseContainer.storage_service]
                 ):
        super().__init__()
        self.__storage_service = storage_service

    def post(self, request, entity_name: str) -> JsonResponse:
        new_record = self.__storage_service.update_entity_type(request, entity_name)
        return JsonResponse(new_record, status=201)
