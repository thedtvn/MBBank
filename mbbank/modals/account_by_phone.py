from .base import BaseResponseModal, Account
from typing import List


class AccountByPhoneResponseModal(BaseResponseModal):
    """
    Model for the get account by phone response containing a list of accounts and account details.
    """
    accountList: List[Account]
    accountNm: str
    accountNo: str

