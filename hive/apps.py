"""Application config module."""

from django.apps import AppConfig


class HiveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hive'

    def ready(self):
        from hive.di.base_container import BaseContainer
        from hive.di.repository_container import RepositoryContainer

        repository_container = RepositoryContainer()
        base_container = BaseContainer()
        base_container.wire(modules=["hive.controllers.create_controller",
                                     "hive.controllers.delete_controller",
                                     "hive.controllers.storage_controller"
                                     ])
        repository_container.wire(modules=["hive.controllers.create_controller",
                                           "hive.controllers.delete_controller",
                                           "hive.controllers.storage_controller"
                                           ])
