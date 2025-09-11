from dataclasses import dataclass
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class CustomAttributesUseInDTO(ABBaseDTO):
    associatedAccountGroups: list = None
    associatedItemGroups: list = None
    associatedUserGroups: list = None
    required: str = None
    resource: str = None
    unique: str = None
    enabled: str = None


@dataclass(kw_only=True)
class CustomAttributesOptionDTO(ABBaseDTO):
    displayOrder: int = None
    name: str = None


@dataclass(kw_only=True)
class CustomAttributeDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    type: str = None
    minValue: str = None
    maxValue: str = None
    maxLength: str = None
    useIn: list[CustomAttributesUseInDTO] = None
    options: list[CustomAttributesOptionDTO] = None
    encryptData: str = None


@dataclass(kw_only=True)
class CustomAttributesRequestDataDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    type: str = None
    minValue: str = None
    maxValue: str = None
    maxLength: str = None
    useIn: list[CustomAttributesUseInDTO] = None
    options: list = None
    encryptData: str = None


@dataclass(kw_only=True)
class CustomAttributesResponseDTO(ABBaseDTO):
    customAttribute: CustomAttributeDTO = None


@dataclass(kw_only=True)
class CustomAttributesRequestDTO(ABBaseDTO):
    customAttribute: CustomAttributesRequestDataDTO = None
