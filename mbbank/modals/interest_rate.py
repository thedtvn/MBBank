from pydantic import BaseModel

from .base import BaseResponseModal


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

    interestRateList: list[InterestRate]
