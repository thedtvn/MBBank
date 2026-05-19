from typing import Optional

from pydantic import BaseModel

from .base import BaseResponseModal


class ProductProperty(BaseModel):
    """
    Product property model.
    """

    originalDeposit: str
    intervalProfitFund: str
    interestRateType: str
    withdraw: str
    cusType: str
    channel: str


class SavingLimits(BaseModel):
    """
    Saving limits model.
    """

    openMinAmount: int
    withdrawMinAmount: int
    depositMinAmount: int


class SavingInfo(BaseModel):
    """
    Saving info model.
    """

    customerId: str
    productCode: str
    savingAccountNumber: str
    interestRate: float
    period: str
    relationName: Optional[str] = None
    maturityDate: str
    subProduct: str
    subProduct2: str
    subProduct3: str
    valueDate: str
    openDate: str
    interestLiquidAccount: str
    nominatedAccount: str
    accountType: str
    currency: str
    intervalInterest: Optional[str] = None
    expectInterestFund: int
    expectInterestEndFund: Optional[int] = None
    guardianId: Optional[str] = None
    beGuardedId: Optional[str] = None
    guardianName: Optional[str] = None
    guardianNationalId: Optional[str] = None
    channel: str
    customerName: str
    isConvert: bool
    isCancelConvert: bool
    isCollateral: bool
    remain: int
    minWithdraw: int
    productName: Optional[str] = None
    maturityInstructions: str
    productProperty: ProductProperty
    savingLimits: list[SavingLimits]
    isDeposit: bool
    isShowDeposit: bool
    isWithDraw: bool
    isTerminate: bool
    isNew: bool
    depositMinAmount: Optional[int] = None
    dateT24: str
    isTerminateOnline: str
    targetSavingName: Optional[str] = None
    type: Optional[str] = None
    isChangeTerminateMethod: Optional[str] = None
    principalAmount: int
    blockAmt: int


class SavingSection(BaseModel):
    """
    Saving section model.
    """

    total: int
    totalExpectInterestFund: int
    data: list[SavingInfo]


class SavingData(BaseModel):
    """
    Saving data model.
    """

    onlineFixedSaving: SavingSection
    branchSaving: SavingSection


class SavingListResponseModal(BaseResponseModal):
    """
    List of savings response model.
    """

    data: SavingData
    isError: bool
