from dataclasses import dataclass
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class ReportLoginRequestDTO(ABBaseDTO):
    email: str = None
    password: str = None


@dataclass(kw_only=True)
class ReportChangePasswordRequestDTO(ABBaseDTO):
    email: str = None
    currentPassword: str = None
    newPassword: str = None


@dataclass(kw_only=True)
class ReportChangePasswordResponseDTO(ABBaseDTO):
    message: str = None


@dataclass(kw_only=True)
class ReportLoginPortalDTO(ABBaseDTO):
    account: str = None
    displayName: str = None
    uuid: str = None


@dataclass(kw_only=True)
class ReportLoginUserDTO(ABBaseDTO):
    type: str = None
    name: str = None
    emailAddress: str = None
    imageUri: str = None
    grantAccessPortal: str = None
    portals: list[ReportLoginPortalDTO] = None


@dataclass(kw_only=True)
class ReportLoginResponseDTO(ABBaseDTO):
    user: ReportLoginUserDTO = None