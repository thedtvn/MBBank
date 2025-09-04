from .base import BaseResponseModal
from pydantic import BaseModel
from typing import List, Optional, Union


class BeneficiaryPayment(BaseModel):
    """
    Model representing a beneficiary for payments.
    """
    name: Optional[str] = None
    value1: Optional[str] = None
    value2: Optional[str] = None
    serviceCode: Optional[str] = None
    providerCode: Optional[str] = None
    custId: Optional[str] = None
    cifId: Optional[str] = None
    valueType: Optional[str] = None
    providerCode2: Optional[str] = None
    providerCode3: Optional[str] = None
    serviceType: Optional[str] = None
    providerNameVi: Optional[str] = None
    providerNameEn: Optional[str] = None
    paymentDateLatest: Optional[str] = None

class BeneficiaryTransfer(BaseModel):
    """
    Model representing a beneficiary for transfers.
    """
    id: Optional[str] = None
    accountNo: Optional[str] = None
    name: Optional[str] = None
    alias: Optional[str] = None
    currency: Optional[str] = None
    isNotifyBen: Optional[str] = None
    notifyBenValue: Optional[str] = None
    domesticType: Optional[str] = None
    domesticIbps: Optional[str] = None
    domesticIbpsDetail: Optional[str] = None
    domesticIbpsCode: Optional[str] = None
    domesticIbpsName: Optional[str] = None
    domesticIbpsDirectCode: Optional[str] = None
    domesticIbpsIndirectCode: Optional[str] = None
    stateCode: Optional[str] = None
    stateName: Optional[str] = None
    branchCode: Optional[str] = None
    branchName: Optional[str] = None
    domesticFast: Optional[str] = None
    domesticFastName: Optional[str] = None
    domesticFastCode: Optional[str] = None
    isCard: Optional[str] = None
    bankCode: Optional[str] = None
    type: Optional[str] = None
    clazz: Optional[str] = None
    institution: Optional[str] = None
    custId: Optional[str] = None
    spiUserCode: Optional[str] = None
    cardId: Optional[str] = None

class BeneficiaryListResponseModal(BaseResponseModal):
    """
    Model representing the response for a list of beneficiaries.
    if transactionType is "TRANSFER", the list contains BeneficiaryTransfer objects.
    if transactionType is "PAYMENT", the list contains BeneficiaryPayment objects.
    """
    favorBeneficiaryList: List[Union[BeneficiaryTransfer, BeneficiaryPayment]]