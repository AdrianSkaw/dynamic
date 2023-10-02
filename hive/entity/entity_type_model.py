from django.db import models


class EntityType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=255, unique=True)
    id = models.AutoField(primary_key=True, auto_created=True)
    file_name = models.CharField(max_length=255,
                                 unique=True)  # TODO - remove this field, because provider will be responsible for this
