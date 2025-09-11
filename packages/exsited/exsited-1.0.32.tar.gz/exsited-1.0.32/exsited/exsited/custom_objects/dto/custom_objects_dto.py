from dataclasses import dataclass

from exsited.exsited.common.dto.common_dto import CustomAttributesDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class CustomObjectDataDTO(ABBaseDTO):
    uuid: str = None
    name: str = None
    entity: str = None
    type: str = None
    values: str = None

    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None
    link: str = None
    version: str = None
    attributes: list[CustomAttributesDTO] = None


@dataclass(kw_only=True)
class CustomObjectsListDTO(ABBaseDTO):
    customObjects: list[CustomObjectDataDTO] = None


@dataclass(kw_only=True)
class CustomObjectsDetailsDTO(ABBaseDTO):
    customObject: CustomObjectDataDTO = None

