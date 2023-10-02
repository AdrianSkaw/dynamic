from hive.entity_field_type.configuration.config_fields_input import ConfigFieldsInput


class ConfigBuilder:
    def __init__(self):
        self.__configs = []

    def add(self, name: str, _type: str, default, required: bool = False):
        config = ConfigFieldsInput(name=name, type=_type, default=default, required=required)
        self.__configs.append(config)

    def get(self) -> list:
        return self.__configs
