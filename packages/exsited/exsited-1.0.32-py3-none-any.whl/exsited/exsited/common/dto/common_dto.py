from dataclasses import dataclass, field
from exsited.sdlize.ab_base_dto import ABBaseDTO
from typing import Any, Union

@dataclass(kw_only=True)
class CurrencyDTO(ABBaseDTO):
    uuid: str = None
    name: str = None
    link: str = None


@dataclass(kw_only=True)
class TimeZoneDTO(ABBaseDTO):
    uuid: str = None
    name: str = None
    link: str = None


@dataclass(kw_only=True)
class TaxDTO(ABBaseDTO):
    uuid: str = None
    code: str = None
    rate: str = None
    link: str = None

    amount: str = None


@dataclass(kw_only=True)
class PaginationDTO(ABBaseDTO):
    records: int = None
    limit: int = None
    offset: int = None
    previousPage: str = None
    nextPage: str = None


@dataclass(kw_only=True)
class AddressDTO(ABBaseDTO):
    addressLine1: str = None
    addressLine2: str = None
    addressLine3: str = None
    addressLine4: str = None
    addressLine5: str = None
    postCode: str = None
    city: str = None
    state: str = None
    country: str = None
    isDefaultBilling: bool = None
    isDefaultShipping: bool = None
    uuid: str = None

    name: str = None


@dataclass(kw_only=True)
class ShippingProfileDTO(ABBaseDTO):
    uuid: str = None
    status: str = None
    name: str = None
    displayName: str = None
    description: str = None
    invoiceNote: str = None
    type: str = None
    fixedAmount: str = None
    isTaxExempt: str = None
    isTaxInclusive: str = None
    taxConfiguration: TaxDTO = None
    accountingCode: str = None


@dataclass(kw_only=True)
class CustomAttributeFileDTO(ABBaseDTO):
    id: str = None
    name: str = None
    size: str = None
    link: str = None


@dataclass(kw_only=True)
class CustomAttributesDTO(ABBaseDTO):
    name: str
    value: Any = field(default=None)

    def __post_init__(self):
        # Handle case 1: value is a list of dictionaries (CustomAttributeFileDTO)
        if isinstance(self.value, list):
            try:
                # Check if the first element is a dictionary
                if self.value and isinstance(self.value[0], dict):
                    self.value = [CustomAttributeFileDTO(**item) for item in self.value]
            except Exception as e:
                pass

        # Handle case 2: value is a list of strings
        elif isinstance(self.value, list):
            try:
                if self.value and isinstance(self.value[0], str):
                    self.value = self.value
            except Exception as e:
                pass

        # Handle case 3: value is a string
        elif isinstance(self.value, str):
            self.value = self.value


@dataclass(kw_only=True)
class CustomObjectDTO(ABBaseDTO):
    name: str = None
    uuid: str = None
    link: str = None


@dataclass(kw_only=True)
class CustomFormsDTO(ABBaseDTO):
    uuid: str = None
    name: str = None


@dataclass(kw_only=True)
class DeleteResponseDTO(ABBaseDTO):
    success: str = None
    statusCode: str = None
