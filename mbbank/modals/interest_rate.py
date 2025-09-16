from .base import BaseResponseModal
from pydantic import BaseModel
from typing import List

class InterestRate(BaseModel):
    productCode: str
    productName: str
    currency: str
    period: str
    amountMin: str
    amountMax: str
    interestRate: str
    region: str


class InterestRateResponseModal(BaseResponseModal):
    interestRateList: List[InterestRate]
