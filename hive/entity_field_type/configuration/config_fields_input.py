from typing import Any

from pydantic import BaseModel


class ConfigFieldsInput(BaseModel):
    name: str
    type: str
    default: Any
    required: bool
