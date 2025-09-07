from .base import BaseResponseModal
from typing import List, Any


class LoanListResponseModal(BaseResponseModal):
    """
    List of loans response model.
    """
    totalLoan: str
    onlineLoansList: List[Any] # I don't know the structure of the loan, so I use Any ( PR welcome )
    olaTotalBalance: str
    branchAccountList: List[Any] # I don't know the structure of the branchAccountList in loan, so I use Any ( PR welcome )
    lbaTotalBalance: str
    currencyEquivalent: str
