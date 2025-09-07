from .base import BaseResponseModal, Account
from typing import List


class BalanceResponseModal(BaseResponseModal):
    """
    Model for the balance response containing lists of accounts and total balances.
    """
    acct_list: List[Account]
    internationalAcctList: List[Account]
    totalBalanceEquivalent: str
    currencyEquivalent: str
