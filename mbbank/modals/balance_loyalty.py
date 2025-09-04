from typing import List
from .base import BaseResponseModal
from pydantic import BaseModel


class BalanceDTO(BaseModel):
    """
    DTO for balance details in loyalty account
    """
    totalHoldingBalance: str
    totalRedeemableBalance: str
    totalBalance: str
    poolId: str


class BalanceLoyalty(BaseModel):
    """
    Model for loyalty balance information
    """
    cif: str
    fullName: str
    loyaltyAccountStatus: str
    cmt: str
    balanceDTO: List[BalanceDTO]


class BalanceLoyaltyResponseModal(BaseResponseModal):
    """
    Response model for loyalty balance API
    """
    bodyBalanceLoyalty: BalanceLoyalty
