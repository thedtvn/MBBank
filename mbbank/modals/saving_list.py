from .base import BaseResponseModal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class SavingInfo(BaseModel):
    """
    Saving info model.
    """
    accountNumber: str
    principalAmount: str
    currency: str
    allowOnlineTerminate: str
    productName: str
    tenor: str
    period: str
    blockedAmount: str
    isSendMore: str
    category: str
    nominatedAccount: str
    accountName: str
    closeDate: Optional[str] = None
    openDate: Optional[str] = None
    rate: str
    subProduct: Optional[str] = None
    productDetail: Optional[str] = None
    accruedInterestAmount: Optional[str] = None
    valueDate: Optional[str] = None
    maturityDate: Optional[str] = None
    ratePreClose: Optional[str] = None
    interestPreClose: Optional[str] = None
    additionInfo: Optional[Dict[str, Any]] = None
    isConvert: Optional[bool] = None
    cancelConvert: Optional[bool] = None

class SavingListResponseModal(BaseResponseModal):
    """
    List of savings response model.
    """
    osaList: List[SavingInfo]
    sbaList: List[SavingInfo]
    osaTotalBalanceEquivalent: str
    sbaTotalBalanceEquivalent: str
    currencyEquivalent: str
