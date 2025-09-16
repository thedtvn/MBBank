from .base import BaseResponseModal
from pydantic import BaseModel
from typing import Optional, List


class CardTransaction(BaseModel):
    """Model representing a single card transaction."""
    postingDate: str
    transactionDate: str
    accountNo: str
    creditAmount: str
    debitAmount: str
    currency: str
    description: str
    availableBalance: Optional[str] = None
    beneficiaryAccount: Optional[str] = None
    refNo: Optional[str] = None
    benAccountName: Optional[str] = None
    bankName: Optional[str] = None
    benAccountNo: Optional[str] = None
    dueDate: Optional[str] = None
    docId: Optional[str] = None
    transactionType: Optional[str] = None


class CardTransactionsResponseModal(BaseResponseModal):
    """Response model for a list of card transactions."""
    transactionHistoryList: List[CardTransaction]
