from dataclasses import dataclass
from typing import Literal


@dataclass
class FieldInfo:
    name: str
    type_name: str

@dataclass
class Tag:
    id: str
    name: str

@dataclass
class Route:
    id: str
    name: str

@dataclass
class SchemaNode:
    id: str
    name: str
    fields: list[FieldInfo]
    is_model: bool = False  # mapping to entities such as orm model

@dataclass
class Link:
    source: str
    source_origin: str  # internal relationship
    target: str
    target_origin: str
    type: Literal['child', 'parent', 'entry', 'subset']
