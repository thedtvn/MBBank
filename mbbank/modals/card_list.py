from .base import BaseResponseModal
from typing import List, Optional
from pydantic import BaseModel

class Card(BaseModel):
    """
    Model representing a single card with its details.
    """
    id: Optional[int]
    acctNm: Optional[str]
    acctNo: Optional[str]
    alwOverLmtPerDay: Optional[str]
    alwOverNoTrxPerDay: Optional[str]
    billingDt: Optional[str]
    cardCatCd: Optional[str]
    cardFlag: Optional[str]
    cardLvl: Optional[str]
    cardNm: Optional[str]
    cardNo: Optional[str]
    cardPrdCd: Optional[str]
    cardTyp: Optional[str]
    ccyCd: Optional[str]
    creditLmt: Optional[int]
    hostCustId: Optional[str]
    isAccsEbanking: Optional[str]
    orgUnitCd: Optional[str]
    pmryCardNm: Optional[str]
    pmryCardNo: Optional[str]
    prdTypCd: Optional[str]
    splmtryFlag: Optional[str]
    sts: Optional[str]
    stsCard: Optional[str]
    stsInetUsage: Optional[str]


class CardListResponseModal(BaseResponseModal):
    """
    Model for the card list response containing lists of cards.
    """
    cardList: List[Card]
    cardClosed: List[Card]
    cardOther: List[Card]
