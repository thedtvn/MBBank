from typing import List, Optional
from .base import BaseResponseModal
from pydantic import BaseModel


class Bank(BaseModel):
    """
    Model representing a bank's information.
    """
    bankId: str
    bankName: str
    bankCode: str
    smlCode: str
    citadCode: Optional[str]
    indirectCitadCode: str
    typeTransfer: str
    isFreeFeeTransferFixAmt: Optional[str]
    isFreeFeeTransferFixAmt2: Optional[str]
    domBankIbps: Optional[str]
    isTransferHO: Optional[str]
    bankNameEN: str
    bankNameKOR: str


class BankListResponseModal(BaseResponseModal):
    """
    Response model for a list of banks.
    """
    listBank: List[Bank]