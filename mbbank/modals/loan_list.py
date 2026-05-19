from typing import Any

from .base import BaseResponseModal


class LoanListResponseModal(BaseResponseModal):
    """
    List of loans response model.
    """

    totalLoan: str
    onlineLoansList: list[Any]  # I don't know the structure of the loan, so I use Any ( PR welcome )
    olaTotalBalance: str
    branchAccountList: list[
        Any
    ]  # I don't know the structure of the branchAccountList in loan, so I use Any ( PR welcome )
    lbaTotalBalance: str
    currencyEquivalent: str
