class RequestData:
    def __init__(self, data):
        self.name = data.get('name')
        self.fields = data.get('fields')
        self.identity = data.get('identity')
        self.primary_keys = data.get('primary_keys')
        self.entity_type = data.get('type')
