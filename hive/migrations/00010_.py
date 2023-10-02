# Generated by Django 4.1.7 on 2023-03-29 12:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('hive', '0009_'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                ("INSERT INTO hive_entityfieldtype(id, name, class_name, sql_type) VALUES(%s,%s,%s,%s)",
                 [1, 'int', 'IntEntityFieldType', 'int']),
                ("INSERT INTO hive_entityfieldtype(id, name, class_name, sql_type) VALUES(%s,%s,%s,%s)",
                 [2, 'str', 'StringEntityFieldType', 'varchar']),
                ("INSERT INTO hive_entityfieldtype(id, name, class_name, sql_type) VALUES(%s,%s,%s,%s)",
                 [3, 'date', 'DateTimeEntityFieldType', 'date']),
                ("INSERT INTO hive_entityfieldtype(id, name, class_name, sql_type) VALUES(%s,%s,%s,%s)",
                 [4, 'float', 'FloatEntityFieldType', 'float']),
                ("INSERT INTO hive_entityfieldtype(id, name, class_name, sql_type) VALUES(%s,%s,%s,%s)",
                 [5, 'ref', 'RefFieldType', 'int'])
            ],
            reverse_sql=[
                ("DELETE FROM hive_entityfieldtype where id=%s;", [1]),
                ("DELETE FROM hive_entityfieldtype where id=%s;", [2]),
                ("DELETE FROM hive_entityfieldtype where id=%s;", [3]),
                ("DELETE FROM hive_entityfieldtype where id=%s;", [4]),
                ("DELETE FROM hive_entityfieldtype where id=%s;", [5])
            ]
        ),
    ]