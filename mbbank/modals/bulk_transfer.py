from typing import Optional

from pydantic import BaseModel

from .base import BaseResponseModal


class AccountTransfer(BaseModel):
    """
    Account transfer info used for bulk transfer.

    Attributes:
        benBankCode (str): smlCode of the destination account get from getBankList e.g. "970422" for MBBank
        amount (int): amount to transfer
        creditAccount (str): destination account number
        customerName (Optional[str]): destination account name if not provided will be fetched from MBBank
        description (str): transfer message
    """

    benBankCode: str
    amount: int
    creditAccount: str
    customerName: Optional[str] = None
    description: str


class BulkTransferResponseModal(BaseResponseModal):
    """
    Response model for bulk transfer.
    """

    totalAmount: Optional[str] = None
    chargeFee: Optional[str] = None
    fileContent: Optional[str] = None
    totalRow: Optional[int] = None
    bulkId: Optional[str] = None
    authenType: Optional[str] = None
    addInfo: Optional[str] = None


class BulkTransferItemModel(BaseModel):
    """
    Model for each item in bulk transfer status list.
    """

    bulkId: str
    sourceAccount: str
    createdDate: str
    totalTransfer: int
    description: Optional[str]
    status: str
    totalFee: int
    requestId: str
    bulkFileName: Optional[str]


class BulkPaymentStatusResponseModal(BaseResponseModal):
    """
    Response model for bulk payment status.
    """

    bulkPaymentList: list[BulkTransferItemModel]


class BulkPaymentDetailItemModel(BaseModel):
    """
    Model for each item in bulk payment detail list.
    """

    detailDestNumber: str
    detailDestName: str
    detailBenBankCd: str
    detailAmount: str
    detailChargeAmount: str
    detailDescription: Optional[str]
    status: str
    errorCode: str
    errorMessage: Optional[str]
    errorDetail: Optional[str]
    ft: Optional[str]
    refundTransactionFT: Optional[str]
    totalTransactionFT: Optional[str]
    totalAmount: Optional[str]
    sourceAccount: Optional[str]
    sourceName: Optional[str]
    time: Optional[str]


class BulkPaymentDetailResponseModal(BaseResponseModal):
    """
    Response model for bulk payment detail.
    """

    bulkPaymentDataDetail: list[BulkPaymentDetailItemModel]
    totalRecords: Optional[int]
    totalPages: Optional[int]
    currentPage: Optional[int]
    pageSize: Optional[int]
