from typing import Optional
from pydantic import BaseModel

__all__ = ["BaseResponseModal", "Account"]

class BaseResponseModal(BaseModel):
    refNo: str

class Account(BaseModel):
    """
    Model for individual account details.
    """
    hostCustId: Optional[str]
    acctNo: str
    acctAlias: Optional[str]
    acctNm: str
    acctTypCd: Optional[str]
    ccyCd: Optional[str]
    currentBalance: Optional[str]
    cardNumber: Optional[str]
    cardProduct: Optional[str]
    isCard: Optional[str]
    cardType: Optional[str]
    category: Optional[str]
    cardCreditLimit: Optional[str]
    isDefault: Optional[str]
    subCategory: Optional[str]
    t24AccountType: Optional[str]
    authorizationBalance: Optional[str] = None # account_by_phone not have this field
    authorizationLmtBalance: Optional[str] = None # account_by_phone not have this field
    isPostpaidQr: Optional[str]
