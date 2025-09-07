from .base import BaseResponseModal
from typing import List
from pydantic import BaseModel

class Transaction(BaseModel):
    """
    Transaction info model.
    """
    postingDate: str
    transactionDate: str
    accountNo: str
    creditAmount: str
    debitAmount: str
    currency: str
    description: str
    addDescription: str
    availableBalance: str
    beneficiaryAccount: str
    refNo: str
    benAccountName: str
    bankName: str
    benAccountNo: str
    dueDate: str
    docId: str
    transactionType: str
    pos: str
    tracingType: str


class TransactionHistoryResponseModal(BaseResponseModal):
    """
    List of transaction history response model.
    """
    transactionHistoryList: List[Transaction]
