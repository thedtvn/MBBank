from .base import BaseResponseModal
from typing import Optional
from pydantic import BaseModel

class SavingDetail(BaseModel):
    """Model representing the details of a saving account."""
    accountNumber: Optional[str] = None
    savingInfoAtTime: str
    savingsAccountNo: str
    productName: str
    productCode: str
    currency: str
    principalAmount: str
    principalAmountEquiv: str
    startDate: str
    maturityDate: str
    interestRate: str
    tenor: str
    outstandingInterest: str
    totalMaturityAmount: str
    accruedInterestAmount: str
    maturityInstructions: str
    holdAmount: str
    interestPaymentType: str
    beneficiaryAccount: str

class SavingDetailResponseModal(BaseResponseModal):
    """Saving detail response model."""
    detailSaving: SavingDetail
