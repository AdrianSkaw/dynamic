from django.db import models


class EntityFieldType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=255, unique=True)
    sql_type = models.CharField(max_length=255, unique=False, default='')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'hive_entityfieldtype'
