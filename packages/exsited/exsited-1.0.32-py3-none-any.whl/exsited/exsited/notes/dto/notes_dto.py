from dataclasses import dataclass, field

from exsited.exsited.common.dto.common_dto import PaginationDTO
from exsited.sdlize.ab_base_dto import ABBaseDTO


@dataclass(kw_only=True)
class FileDTO(ABBaseDTO):
    uuid: str = None
    name: str = None
    version: str = None

@dataclass(kw_only=True)
class NoteDataDTO(ABBaseDTO):
    uuid: str = None
    version: str = None
    content: str = None
    files: list[FileDTO] = None
    createdBy: str = None
    createdOn: str = None
    lastUpdatedBy: str = None
    lastUpdatedOn: str = None


@dataclass(kw_only=True)
class OrderNoteDataDTO(ABBaseDTO):
    notes: list[NoteDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class ItemNoteDataDTO(ABBaseDTO):
    notes: list[NoteDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class InvoiceNoteDataDTO(ABBaseDTO):
    notes: list[NoteDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class PaymentNoteDataDTO(ABBaseDTO):
    notes: list[NoteDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class PurchaseOrderNoteDataDTO(ABBaseDTO):
    notes: list[NoteDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceNoteDataDTO(ABBaseDTO):
    notes: list[NoteDataDTO] = None
    pagination: PaginationDTO = None


@dataclass(kw_only=True)
class OrderNoteDetailsDTO(ABBaseDTO):
    order: OrderNoteDataDTO = None


@dataclass(kw_only=True)
class ItemNoteDetailsDTO(ABBaseDTO):
    item: ItemNoteDataDTO = None


@dataclass(kw_only=True)
class InvoiceNoteDetailsDTO(ABBaseDTO):
    invoice: InvoiceNoteDataDTO = None


@dataclass(kw_only=True)
class PaymentNoteDetailsDTO(ABBaseDTO):
    payment: PaymentNoteDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderDetailsDTO(ABBaseDTO):
    purchaseOrder: PurchaseOrderNoteDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceDetailsDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceNoteDataDTO = None


@dataclass(kw_only=True)
class OrderNoteUuidDataDTO(ABBaseDTO):
    note: NoteDataDTO = None


@dataclass(kw_only=True)
class ItemNoteUuidDataDTO(ABBaseDTO):
    note: NoteDataDTO = None


@dataclass(kw_only=True)
class InvoiceNoteUuidDataDTO(ABBaseDTO):
    note: NoteDataDTO = None


@dataclass(kw_only=True)
class PaymentNoteUuidDataDTO(ABBaseDTO):
    note: NoteDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderNoteUuidDataDTO(ABBaseDTO):
    note: NoteDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceNoteUuidDataDTO(ABBaseDTO):
    note: NoteDataDTO = None


@dataclass(kw_only=True)
class OrderNoteUuidDetailsDTO(ABBaseDTO):
    order: OrderNoteUuidDataDTO = None


@dataclass(kw_only=True)
class ItemNoteUuidDetailsDTO(ABBaseDTO):
    item: ItemNoteUuidDataDTO = None


@dataclass(kw_only=True)
class InvoiceNoteUuidDetailsDTO(ABBaseDTO):
    invoice: InvoiceNoteUuidDataDTO = None


@dataclass(kw_only=True)
class PaymentNoteUuidDetailsDTO(ABBaseDTO):
    payment: PaymentNoteUuidDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderNoteUuidDetailsDTO(ABBaseDTO):
    purchaseOrder: PurchaseOrderNoteUuidDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceNoteUuidDetailsDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceNoteUuidDataDTO = None


@dataclass(kw_only=True)
class NoteFileDataDTO(ABBaseDTO):
    files: list[FileDTO] = None


@dataclass(kw_only=True)
class OrderNoteUuidFileDataDTO(ABBaseDTO):
    note: NoteFileDataDTO = None


@dataclass(kw_only=True)
class ItemNoteUuidFileDataDTO(ABBaseDTO):
    note: NoteFileDataDTO = None


@dataclass(kw_only=True)
class InvoiceNoteUuidFileDataDTO(ABBaseDTO):
    note: NoteFileDataDTO = None


@dataclass(kw_only=True)
class PaymentNoteUuidFileDataDTO(ABBaseDTO):
    note: NoteFileDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderUuidFileDataDTO(ABBaseDTO):
    note: NoteFileDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceUuidFileDataDTO(ABBaseDTO):
    note: NoteFileDataDTO = None


@dataclass(kw_only=True)
class OrderNoteUuidFileDetailsDTO(ABBaseDTO):
    order: OrderNoteUuidFileDataDTO = None


@dataclass(kw_only=True)
class ItemNoteUuidFileDetailsDTO(ABBaseDTO):
    item: ItemNoteUuidFileDataDTO = None


@dataclass(kw_only=True)
class InvoiceNoteUuidFileDetailsDTO(ABBaseDTO):
    invoice: InvoiceNoteUuidFileDataDTO = None


@dataclass(kw_only=True)
class PaymentNoteUuidFileDetailsDTO(ABBaseDTO):
    payment: PaymentNoteUuidFileDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderUuidFileDetailsDTO(ABBaseDTO):
    purchaseOrder: PurchaseOrderUuidFileDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceUuidFileDetailsDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceUuidFileDataDTO = None


@dataclass(kw_only=True)
class NoteFileUuidDataDTO(ABBaseDTO):
    file: FileDTO = None


@dataclass(kw_only=True)
class OrderNoteUuidFileUuidDataDTO(ABBaseDTO):
    note: NoteFileUuidDataDTO = None


@dataclass(kw_only=True)
class ItemNoteUuidFileUuidDataDTO(ABBaseDTO):
    note: NoteFileUuidDataDTO = None


@dataclass(kw_only=True)
class InvoiceNoteUuidFileUuidDataDTO(ABBaseDTO):
    note: NoteFileUuidDataDTO = None


@dataclass(kw_only=True)
class PaymentNoteUuidFileUuidDataDTO(ABBaseDTO):
    note: NoteFileUuidDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderNoteUuidFileUuidDataDTO(ABBaseDTO):
    note: NoteFileUuidDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceNoteUuidFileUuidDataDTO(ABBaseDTO):
    note: NoteFileUuidDataDTO = None


@dataclass(kw_only=True)
class OrderNoteUuidFileUuidDetailsDTO(ABBaseDTO):
    order: OrderNoteUuidFileUuidDataDTO = None


@dataclass(kw_only=True)
class ItemNoteUuidFileUuidDetailsDTO(ABBaseDTO):
    item: ItemNoteUuidFileUuidDataDTO = None


@dataclass(kw_only=True)
class InvoiceNoteUuidFileUuidDetailsDTO(ABBaseDTO):
    invoice: InvoiceNoteUuidFileUuidDataDTO = None


@dataclass(kw_only=True)
class PaymentNoteUuidFileUuidDetailsDTO(ABBaseDTO):
    payment: PaymentNoteUuidFileUuidDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderNoteUuidFileUuidDetailsDTO(ABBaseDTO):
    purchaseOrder: PurchaseOrderNoteUuidFileUuidDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceNoteUuidFileUuidDetailsDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceNoteUuidFileUuidDataDTO = None


@dataclass(kw_only=True)
class OrderNoteResponseDataDTO(ABBaseDTO):
    notes: NoteDataDTO = None


@dataclass(kw_only=True)
class ItemNoteResponseDataDTO(ABBaseDTO):
    notes: NoteDataDTO = None


@dataclass(kw_only=True)
class InvoiceNoteResponseDataDTO(ABBaseDTO):
    notes: NoteDataDTO = None


@dataclass(kw_only=True)
class PaymentNoteResponseDataDTO(ABBaseDTO):
    notes: NoteDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderNoteResponseDataDTO(ABBaseDTO):
    notes: NoteDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceNoteResponseDataDTO(ABBaseDTO):
    notes: NoteDataDTO = None


@dataclass(kw_only=True)
class OrderNoteResponseDetailsDTO(ABBaseDTO):
    order: OrderNoteResponseDataDTO = None


@dataclass(kw_only=True)
class ItemNoteResponseDetailsDTO(ABBaseDTO):
    item: ItemNoteResponseDataDTO = None


@dataclass(kw_only=True)
class InvoiceNoteResponseDetailsDTO(ABBaseDTO):
    invoice: InvoiceNoteResponseDataDTO = None


@dataclass(kw_only=True)
class PaymentNoteResponseDetailsDTO(ABBaseDTO):
    payment: PaymentNoteResponseDataDTO = None


@dataclass(kw_only=True)
class PurchaseOrderNoteResponseDetailsDTO(ABBaseDTO):
    purchaseOrder: PurchaseOrderNoteResponseDataDTO = None


@dataclass(kw_only=True)
class PurchaseInvoiceNoteResponseDetailsDTO(ABBaseDTO):
    purchaseInvoice: PurchaseInvoiceNoteResponseDataDTO = None
