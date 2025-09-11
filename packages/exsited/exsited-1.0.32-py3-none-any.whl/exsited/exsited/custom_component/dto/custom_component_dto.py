from dataclasses import dataclass
from typing import List, Dict
from exsited.sdlize.ab_base_dto import ABBaseDTO

@dataclass(kw_only=True)
class AttributeDTO(ABBaseDTO):
    name: str = None
    value: str = None

@dataclass(kw_only=True)
class ParentDTO(ABBaseDTO):
    type: str = None
    id: str = None

@dataclass(kw_only=True)
class AttributeGroupDTO(ABBaseDTO):
    uuid: str = None
    name: str = None
    attributes: list[AttributeDTO] = None

@dataclass(kw_only=True)
class CustomObjectDTO(ABBaseDTO):
    uuid: str = None
    name: str = None
    link: str = None

@dataclass(kw_only=True)
class CustomComponentDataDTO(ABBaseDTO):
    status: str = None
    id: str = None
    parents: list[ParentDTO] = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    uuid: str = None
    version: str = None
    attributes: list[AttributeDTO] = None
    attributeGroups: list[AttributeGroupDTO] = None
    customObjects: list[CustomObjectDTO] = None

@dataclass(kw_only=True)
class PaginationDTO(ABBaseDTO):
    records: str = None
    limit: str = None
    offset: str = None
    previousPage: str = None
    nextPage: str = None

@dataclass(kw_only=True)
class CustomComponentResponseDTO(ABBaseDTO):
    name: list[CustomComponentDataDTO] = None
    pagination: PaginationDTO = None
