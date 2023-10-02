class EntityFieldTypeProvider:

    def __init__(self
                 , int_entity_field_type
                 , string_entity_field_type
                 , datetime_entity_field_type
                 , float_entity_field_type
                 , ref_field_type
                 , money_field_type
                 ):  # TODO: Create register and move this to it
        self.__items = {
            'int': int_entity_field_type
            , 'str': string_entity_field_type
            , 'date': datetime_entity_field_type
            , 'float': float_entity_field_type
            , 'ref': ref_field_type
            , 'money': money_field_type
        }

    def get(self, entity_field_type: str):
        if entity_field_type not in self.__items:
            raise ValueError(f'Invalid entity field type: {entity_field_type}')
        return self.__items[entity_field_type]
