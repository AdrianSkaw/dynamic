from typing import Any

from pydantic import BaseModel


class Field(BaseModel):
    name: str
    type: str
    config: dict
    nullable: bool
    default: Any
