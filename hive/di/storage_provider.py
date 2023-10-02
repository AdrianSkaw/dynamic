class StorageProvider:

    def __init__(self, update_storage):
        self.__items = {
            'UpdateStorage': update_storage
        }

    def get(self, storage_class_name: str):
        if storage_class_name not in self.__items:
            raise ValueError(f'Invalid storage class name: {storage_class_name}')
        return self.__items[storage_class_name]
