class FormatNotSupportedException(Exception):
    def __init__(self, data):
        message = f"Format not supported for data: {data}"
        super().__init__(message)