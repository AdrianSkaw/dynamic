from django.db import models

from hive.entity.entity_type_model import EntityType


class Entity(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=50, unique=True)
    fields = models.JSONField(default=list)
    identity = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    primary_keys = models.JSONField(max_length=50, default=list, unique=True)
    type = models.ForeignKey(EntityType, on_delete=models.CASCADE, to_field='id')
