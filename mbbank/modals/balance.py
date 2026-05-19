from .base import Account, BaseResponseModal


class BalanceResponseModal(BaseResponseModal):
    """
    Model for the balance response containing lists of accounts and total balances.
    """

    acct_list: list[Account]
    internationalAcctList: list[Account]
    totalBalanceEquivalent: str
    currencyEquivalent: str
