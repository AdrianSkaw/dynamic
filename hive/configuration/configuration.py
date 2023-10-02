import os

from dotenv import load_dotenv

load_dotenv('.env')


class Configuration:

    def __init__(self):
        self.__hive_user = os.getenv("HIVE_USER")
        self.__hive_pass = os.getenv("HIVE_PASS")
        self.__schema = os.getenv("STORAGE_SCHEMA")

    def get_hive_user(self):
        return self.__hive_user

    def get_hive_pass(self):
        return self.__hive_pass

    def get_schema(self):
        return self.__schema
