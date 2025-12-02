from .base import BaseResponseModal, Account
from typing import List, Optional, Any


class AccountByPhoneResponseModal(BaseResponseModal):
    """
    Model for the get account by phone response containing a list of accounts and account details.
    """

    accountList: List[Account]
    accountNm: str
    accountNo: str


class AccountNameResponseModal(BaseResponseModal):
    """
    Model for the get account name response
    """

    benName: str
    transferType: str
    riskCode: Optional[str]
    riskMessage: Optional[str]
    category: Optional[str]
    accountType: Optional[str]
    bankCode: Optional[str]
    benT24AcctNumber: Optional[str]
    queryChannel: Optional[str]


class ATMAccountNameResponseModal(BaseResponseModal):
    """
    Model for the get ATM account name response
    """

    benName: Optional[str]
    category: Optional[Any] = None
