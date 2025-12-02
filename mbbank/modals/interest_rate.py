from .base import BaseResponseModal
from pydantic import BaseModel
from typing import List


class InterestRate(BaseModel):
    """
    Interest Rate Modal
    """

    productCode: str
    productName: str
    currency: str
    period: str
    amountMin: str
    amountMax: str
    interestRate: str
    region: str


class InterestRateResponseModal(BaseResponseModal):
    """
    Interest Rate Response Modal
    """

    interestRateList: List[InterestRate]
