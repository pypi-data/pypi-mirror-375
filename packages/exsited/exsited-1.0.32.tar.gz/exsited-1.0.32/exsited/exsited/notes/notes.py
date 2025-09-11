from exsited.exsited.account.dto.account_dto import AccountNoteResponseDetailsDTO, AccountDetailsDTO, \
    AccountNoteDetailsDTO, AccountAddressUuidDetailsDTO, AccountNoteUuidDetailsDTO, AccountNoteUuidFileDetailsDTO, \
    AccountNoteUuidFileUuidDetailsDTO
from exsited.exsited.common.common_enum import SortDirection
from exsited.common.sdk_util import SDKUtil
from exsited.exsited.notes.dto.notes_dto import NoteDataDTO, OrderNoteDetailsDTO, OrderNoteUuidDetailsDTO, \
    OrderNoteUuidFileDetailsDTO, OrderNoteUuidFileUuidDetailsDTO, OrderNoteResponseDetailsDTO, ItemNoteDetailsDTO, \
    ItemNoteUuidDetailsDTO, ItemNoteUuidFileDetailsDTO, ItemNoteUuidFileUuidDetailsDTO, ItemNoteResponseDetailsDTO, \
    InvoiceNoteDetailsDTO, InvoiceNoteUuidDetailsDTO, InvoiceNoteUuidFileDetailsDTO, InvoiceNoteUuidFileUuidDetailsDTO, \
    InvoiceNoteResponseDetailsDTO, PaymentNoteDetailsDTO, PaymentNoteUuidDetailsDTO, PaymentNoteUuidFileDetailsDTO, \
    PaymentNoteUuidFileUuidDetailsDTO, PaymentNoteResponseDetailsDTO, PurchaseOrderDetailsDTO, \
    PurchaseOrderNoteUuidDetailsDTO, PurchaseOrderUuidFileDetailsDTO, PurchaseOrderNoteUuidFileUuidDetailsDTO, \
    PurchaseOrderNoteResponseDetailsDTO, PurchaseInvoiceDetailsDTO, PurchaseInvoiceNoteUuidDetailsDTO, \
    PurchaseInvoiceUuidFileDetailsDTO, PurchaseInvoiceNoteUuidFileUuidDetailsDTO, PurchaseInvoiceNoteResponseDetailsDTO
from exsited.exsited.notes.notes_api_urls import NoteApiUrl
from exsited.http.ab_rest_processor import ABRestProcessor
import mimetypes


class Notes(ABRestProcessor):
    def __init__(self, request_token_dto, file_token_mgr=None):
        super().__init__(request_token_dto, file_token_mgr)

    def note_details(self, uuid: str) -> NoteDataDTO:
        response = self.get(url=NoteApiUrl.NOTE.format(uuid=uuid), response_obj=NoteDataDTO())
        return response

    def account_note_details(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None, param_filters: dict = None) -> AccountNoteDetailsDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=NoteApiUrl.ACCOUNTS_NOTE.format(id=id), params=params, response_obj=AccountNoteDetailsDTO())
        return response

    def order_note_details(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None, param_filters: dict = None) -> OrderNoteDetailsDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=NoteApiUrl.ORDER_NOTE.format(id=id), params=params, response_obj=OrderNoteDetailsDTO())
        return response

    def item_note_details(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None, param_filters: dict = None) -> ItemNoteDetailsDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=NoteApiUrl.ITEM_NOTE.format(id=id), params=params, response_obj=ItemNoteDetailsDTO())
        return response

    def invoice_note_details(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None, param_filters: dict = None) -> InvoiceNoteDetailsDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=NoteApiUrl.INVOICE_NOTE.format(id=id), params=params, response_obj=InvoiceNoteDetailsDTO())
        return response

    def payment_note_details(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None, param_filters: dict = None) -> PaymentNoteDetailsDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=NoteApiUrl.PAYMENT_NOTE.format(id=id), params=params, response_obj=PaymentNoteDetailsDTO())
        return response

    def purchase_order_note_details(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None, param_filters: dict = None) -> PurchaseOrderDetailsDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=NoteApiUrl.PURCHASE_ORDER_NOTE.format(id=id), params=params, response_obj=PurchaseOrderDetailsDTO())
        return response

    def purchase_invoice_note_details(self, id: str, limit: int = None, offset: int = None, direction: SortDirection = None,
             order_by: str = None, param_filters: dict = None) -> PurchaseInvoiceDetailsDTO:
        params = SDKUtil.init_pagination_params(params=param_filters,limit=limit, offset=offset, direction=direction, order_by=order_by)
        response = self.get(url=NoteApiUrl.PURCHASE_INVOICE_NOTE.format(id=id), params=params, response_obj=PurchaseInvoiceDetailsDTO())
        return response

    def note_uuid_details(self, id: str, uuid: str) -> AccountNoteUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.ACCOUNTS_NOTE_UUID.format(id=id, uuid=uuid), response_obj=AccountNoteUuidDetailsDTO())
        return response

    def order_note_uuid_details(self, id: str, uuid: str) -> OrderNoteUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.ORDER_NOTE_UUID.format(id=id, uuid=uuid), response_obj=OrderNoteUuidDetailsDTO())
        return response

    def item_note_uuid_details(self, id: str, uuid: str) -> ItemNoteUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.ITEM_NOTE_UUID.format(id=id, uuid=uuid), response_obj=ItemNoteUuidDetailsDTO())
        return response

    def invoice_note_uuid_details(self, id: str, uuid: str) -> InvoiceNoteUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.INVOICE_NOTE_UUID.format(id=id, uuid=uuid), response_obj=InvoiceNoteUuidDetailsDTO())
        return response

    def payment_note_uuid_details(self, id: str, uuid: str) -> PaymentNoteUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.PAYMENT_NOTE_UUID.format(id=id, uuid=uuid), response_obj=PaymentNoteUuidDetailsDTO())
        return response

    def purchase_order_note_uuid_details(self, id: str, uuid: str) -> PurchaseOrderNoteUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.PURCHASE_ORDER_NOTE_UUID.format(id=id, uuid=uuid), response_obj=PurchaseOrderNoteUuidDetailsDTO())
        return response

    def purchase_invoice_note_uuid_details(self, id: str, uuid: str) -> PurchaseInvoiceNoteUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.PURCHASE_INVOICE_NOTE_UUID.format(id=id, uuid=uuid), response_obj=PurchaseInvoiceNoteUuidDetailsDTO())
        return response

    def note_uuid_files_details(self, id: str, uuid: str) -> AccountNoteUuidFileDetailsDTO:
        response = self.get(url=NoteApiUrl.ACCOUNTS_NOTE_UUID_FILES.format(id=id, uuid=uuid), response_obj=AccountNoteUuidFileDetailsDTO())
        return response

    def order_note_uuid_files_details(self, id: str, uuid: str) -> OrderNoteUuidFileDetailsDTO:
        response = self.get(url=NoteApiUrl.ORDER_NOTE_UUID_FILES.format(id=id, uuid=uuid), response_obj=OrderNoteUuidFileDetailsDTO())
        return response

    def item_note_uuid_files_details(self, id: str, uuid: str) -> ItemNoteUuidFileDetailsDTO:
        response = self.get(url=NoteApiUrl.ITEM_NOTE_UUID_FILES.format(id=id, uuid=uuid), response_obj=ItemNoteUuidFileDetailsDTO())
        return response

    def invoice_note_uuid_files_details(self, id: str, uuid: str) -> InvoiceNoteUuidFileDetailsDTO:
        response = self.get(url=NoteApiUrl.INVOICE_NOTE_UUID_FILES.format(id=id, uuid=uuid), response_obj=InvoiceNoteUuidFileDetailsDTO())
        return response

    def payment_note_uuid_files_details(self, id: str, uuid: str) -> PaymentNoteUuidFileDetailsDTO:
        response = self.get(url=NoteApiUrl.PAYMENT_NOTE_UUID_FILES.format(id=id, uuid=uuid), response_obj=PaymentNoteUuidFileDetailsDTO())
        return response

    def purchase_order_note_uuid_files_details(self, id: str, uuid: str) -> PurchaseOrderUuidFileDetailsDTO:
        response = self.get(url=NoteApiUrl.PURCHASE_ORDER_NOTE_UUID_FILES.format(id=id, uuid=uuid), response_obj=PurchaseOrderUuidFileDetailsDTO())
        return response

    def purchase_invoice_note_uuid_files_details(self, id: str, uuid: str) -> PurchaseInvoiceUuidFileDetailsDTO:
        response = self.get(url=NoteApiUrl.PURCHASE_INVOICE_NOTE_UUID_FILES.format(id=id, uuid=uuid), response_obj=PurchaseInvoiceUuidFileDetailsDTO())
        return response

    def note_uuid_files_uuid_details(self, id: str, uuid: str, file_uuid: str) -> AccountNoteUuidFileUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.ACCOUNTS_NOTE_UUID_FILES_UUID.format(id=id, uuid=uuid,file_uuid=file_uuid), response_obj=AccountNoteUuidFileUuidDetailsDTO())
        return response

    def order_note_uuid_files_uuid_details(self, id: str, uuid: str, file_uuid: str) -> OrderNoteUuidFileUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.ORDER_NOTE_UUID_FILES_UUID.format(id=id, uuid=uuid,file_uuid=file_uuid), response_obj=OrderNoteUuidFileUuidDetailsDTO())
        return response

    def item_note_uuid_files_uuid_details(self, id: str, uuid: str, file_uuid: str) -> ItemNoteUuidFileUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.ITEM_NOTE_UUID_FILES_UUID.format(id=id, uuid=uuid,file_uuid=file_uuid), response_obj=ItemNoteUuidFileUuidDetailsDTO())
        return response

    def invoice_note_uuid_files_uuid_details(self, id: str, uuid: str, file_uuid: str) -> InvoiceNoteUuidFileUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.INVOICE_NOTE_UUID_FILES_UUID.format(id=id, uuid=uuid,file_uuid=file_uuid), response_obj=InvoiceNoteUuidFileUuidDetailsDTO())
        return response

    def payment_note_uuid_files_uuid_details(self, id: str, uuid: str, file_uuid: str) -> PaymentNoteUuidFileUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.PAYMENT_NOTE_UUID_FILES_UUID.format(id=id, uuid=uuid,file_uuid=file_uuid), response_obj=PaymentNoteUuidFileUuidDetailsDTO())
        return response

    def purchase_order_note_uuid_files_uuid_details(self, id: str, uuid: str, file_uuid: str) -> PurchaseOrderNoteUuidFileUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.PURCHASE_ORDER_NOTE_UUID_FILES_UUID.format(id=id, uuid=uuid,file_uuid=file_uuid), response_obj=PurchaseOrderNoteUuidFileUuidDetailsDTO())
        return response

    def purchase_invoice_note_uuid_files_uuid_details(self, id: str, uuid: str, file_uuid: str) -> PurchaseInvoiceNoteUuidFileUuidDetailsDTO:
        response = self.get(url=NoteApiUrl.PURCHASE_INVOICE_NOTE_UUID_FILES_UUID.format(id=id, uuid=uuid,file_uuid=file_uuid), response_obj=PurchaseInvoiceNoteUuidFileUuidDetailsDTO())
        return response

    def add_notes(self, file_urls: list = None, account_id: str = "", datas: str = "") -> AccountNoteResponseDetailsDTO:
        note_data = {
            "note": datas
        }

        files = []

        if file_urls:
            for index, file_url in enumerate(file_urls):
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.ACCOUNTS_NOTE.format(id=account_id),
                data=note_data,
                file=files,
                response_obj=AccountNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()
        else:
            response = self.post(
                url=NoteApiUrl.ACCOUNTS_NOTE.format(id=account_id),
                data=note_data,
                response_obj=AccountNoteResponseDetailsDTO()
            )

        return response

    def order_add_notes(self, file_urls: list = None, order_id: str = "", datas: str = "") -> OrderNoteResponseDetailsDTO:
        note_data = {
            "note": datas
        }

        files = []

        if file_urls:
            for index, file_url in enumerate(file_urls):
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.ORDER_NOTE_ADD.format(id=order_id),
                data=note_data,
                file=files,
                response_obj=OrderNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()
        else:
            response = self.post(
                url=NoteApiUrl.ORDER_NOTE_ADD.format(id=order_id),
                data=note_data,
                response_obj=OrderNoteResponseDetailsDTO()
            )

        return response

    def item_add_notes(self, file_urls: list = None, item_id: str = "", datas: str = "") -> ItemNoteResponseDetailsDTO:

        note_data = {
            "note": datas
        }

        files = []

        if file_urls:
            for index, file_url in enumerate(file_urls):
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.ITEM_NOTE_ADD.format(id=item_id),
                data=note_data,
                file=files,
                response_obj=ItemNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()
        else:
            response = self.post(
                url=NoteApiUrl.ITEM_NOTE_ADD.format(id=item_id),
                data=note_data,
                response_obj=ItemNoteResponseDetailsDTO()
            )

        return response

    def invoice_add_notes(self, file_urls: list = None, invoice_id: str = "",
                          datas: str = "") -> InvoiceNoteResponseDetailsDTO:

        note_data = {
            "note": datas
        }

        files = []

        if file_urls:
            for index, file_url in enumerate(file_urls):
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.INVOICE_NOTE_ADD.format(id=invoice_id),
                data=note_data,
                file=files,
                response_obj=InvoiceNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()
        else:
            response = self.post(
                url=NoteApiUrl.INVOICE_NOTE_ADD.format(id=invoice_id),
                data=note_data,
                response_obj=InvoiceNoteResponseDetailsDTO()
            )

        return response

    def payment_add_notes(self, file_urls: list = None, payment_id: str = "", datas: str = "") -> PaymentNoteResponseDetailsDTO:
        note_data = {
            "note": datas
        }

        files = []

        if file_urls:
            for index, file_url in enumerate(file_urls):
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.PAYMENT_NOTE_ADD.format(id=payment_id),
                data=note_data,
                file=files,
                response_obj=PaymentNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()
        else:
            response = self.post(
                url=NoteApiUrl.PAYMENT_NOTE_ADD.format(id=payment_id),
                data=note_data,
                response_obj=PaymentNoteResponseDetailsDTO()
            )

        return response

    def purchase_order_add_notes(self, file_urls: list = None, purchase_order_id: str = "", datas: str = "") -> PurchaseOrderNoteResponseDetailsDTO:
        note_data = {
            "note": datas
        }

        files = []

        if file_urls:
            for index, file_url in enumerate(file_urls):
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.PURCHASE_ORDER_NOTE_ADD.format(id=purchase_order_id),
                data=note_data,
                file=files,
                response_obj=PurchaseOrderNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()
        else:
            response = self.post(
                url=NoteApiUrl.PURCHASE_ORDER_NOTE_ADD.format(id=purchase_order_id),
                data=note_data,
                response_obj=PurchaseOrderNoteResponseDetailsDTO()
            )

        return response

    def purchase_invoice_add_notes(self, file_urls: list = None, purchase_invoice_id: str = "", datas: str = "") -> PurchaseInvoiceNoteResponseDetailsDTO:
        note_data = {
            "note": datas
        }

        files = []

        if file_urls:
            for index, file_url in enumerate(file_urls):
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.PURCHASE_INVOICE_NOTE_ADD.format(id=purchase_invoice_id),
                data=note_data,
                file=files,
                response_obj=PurchaseInvoiceNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()
        else:
            response = self.post(
                url=NoteApiUrl.PURCHASE_INVOICE_NOTE_ADD.format(id=purchase_invoice_id),
                data=note_data,
                response_obj=PurchaseInvoiceNoteResponseDetailsDTO()
            )

        return response

    def add_notes_uuid(self, file_urls: list, account_id: str, note_uuid: str) -> AccountNoteResponseDetailsDTO:
        files = []

        if file_urls:
            for file_url in file_urls:
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.ACCOUNTS_NOTE_UUID.format(id=account_id, uuid=note_uuid),
                file=files,
                response_obj=AccountNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()

        else:
            raise ValueError("No files provided for upload.")

        return response


    def order_add_notes_uuid(self, file_urls: list, order_id: str, note_uuid:str) -> OrderNoteResponseDetailsDTO:
        files = []

        if file_urls:
            for file_url in file_urls:
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.ORDER_NOTE_UUID_ADD.format(id=order_id, uuid=note_uuid),
                file=files,
                response_obj=OrderNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()

        else:
            raise ValueError("No files provided for upload.")

        return response

    def item_add_notes_uuid(self, file_urls: list, item_id: str, note_uuid:str) -> ItemNoteResponseDetailsDTO:
        files = []

        if file_urls:
            for file_url in file_urls:
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.ITEM_NOTE_UUID_ADD.format(id=item_id, uuid=note_uuid),
                file=files,
                response_obj=ItemNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()

        else:
            raise ValueError("No files provided for upload.")

        return response

    def invoice_add_notes_uuid(self, file_urls: list, invoice_id: str, note_uuid: str) -> InvoiceNoteResponseDetailsDTO:
        files = []

        if file_urls:
            for file_url in file_urls:
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.INVOICE_NOTE_UUID_ADD.format(id=invoice_id, uuid=note_uuid),
                file=files,
                response_obj=InvoiceNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()

        else:
            raise ValueError("No files provided for upload.")

        return response

    def payment_add_notes_uuid(self, file_urls: list, payment_id: str,
                               note_uuid: str) -> PaymentNoteResponseDetailsDTO:
        files = []

        if file_urls:
            for file_url in file_urls:
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.PAYMENT_NOTE_UUID_ADD.format(id=payment_id, uuid=note_uuid),
                file=files,
                response_obj=PaymentNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()

        else:
            raise ValueError("No files provided for upload.")

        return response

    def purchase_order_add_notes_uuid(self, file_urls: list, purchase_order_id: str,
                               note_uuid: str) -> PurchaseOrderNoteResponseDetailsDTO:
        files = []

        if file_urls:
            for file_url in file_urls:
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.PURCHASE_ORDER_NOTE_UUID_ADD.format(id=purchase_order_id, uuid=note_uuid),
                file=files,
                response_obj=PurchaseOrderNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()

        else:
            raise ValueError("No files provided for upload.")

        return response

    def purchase_invoice_add_notes_uuid(self, file_urls: list, purchase_invoice_id: str,
                               note_uuid: str) -> PurchaseInvoiceNoteResponseDetailsDTO:
        files = []

        if file_urls:
            for file_url in file_urls:
                mime_type, _ = mimetypes.guess_type(file_url)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_obj = open(file_url, "rb")
                files.append(('file', (file_url.split("\\")[-1], file_obj, mime_type)))

            response = self.post(
                url=NoteApiUrl.PURCHASE_INVOICE_NOTE_UUID_ADD.format(id=purchase_invoice_id, uuid=note_uuid),
                file=files,
                response_obj=PurchaseInvoiceNoteResponseDetailsDTO()
            )

            for file_tuple in files:
                file_tuple[1][1].close()

        else:
            raise ValueError("No files provided for upload.")

        return response

    def delete_note_uuid_details(self, id: str, uuid: str) -> dict:
        response = self.delete_request(url=NoteApiUrl.ACCOUNTS_NOTE_UUID.format(id=id, uuid=uuid), response_obj={})
        return response
