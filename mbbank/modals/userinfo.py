from .base import BaseResponseModal
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class UserInfoAccountModel(BaseModel):
    """Model representing a user's bank account information."""

    acctNo: Optional[str]
    acctAlias: Optional[str]
    acctNm: Optional[str]
    acctTypCd: Optional[str]
    ccyCd: Optional[str]
    custId: Optional[str]
    hostCustId: Optional[str]
    inactiveSts: Optional[str]
    orgUnitCd: Optional[str]
    isCrdt: Optional[str]
    isDebit: Optional[str]
    isInq: Optional[str]
    currentBalance: Optional[Any]
    isSync: Optional[Any]
    category: Optional[str]
    productType: Optional[str]


class UserInfoCardModel(BaseModel):
    """Model representing a user's card information."""

    id: Optional[Any]
    acctNm: Optional[str]
    acctNo: Optional[str]
    alwOverLmtPerDay: Optional[Any]
    alwOverNoTrxPerDay: Optional[Any]
    billingDt: Optional[Any]
    cardCatCd: Optional[Any]
    cardFlag: Optional[Any]
    cardLvl: Optional[str]
    cardNm: Optional[str]
    cardNo: Optional[str]
    cardPrdCd: Optional[str]
    cardTyp: Optional[str]
    ccyCd: Optional[str]
    creditLmt: Optional[Any]
    hostCustId: Optional[str]
    isAccsEbanking: Optional[Any]
    orgUnitCd: Optional[Any]
    pmryCardNm: Optional[str]
    pmryCardNo: Optional[str]
    prdTypCd: Optional[Any]
    splmtryFlag: Optional[str]
    sts: Optional[str]
    stsCard: Optional[Any]
    stsInetUsage: Optional[str]
    validThrough: Optional[str]
    cardCtkd: Optional[Any]
    branchCode: Optional[Any]
    cardDisplay: Optional[Any]
    amountAvailable: Optional[Any]
    interestRate: Optional[Any]
    type: Optional[Any]
    activeDate: Optional[Any]
    groupDebit: Optional[Any]
    outstandingBalance: Optional[Any]
    totalWithDrawInMonth: Optional[Any]
    maxWithDraw: Optional[Any]
    err: Optional[Any]
    messageErr: Optional[Any]
    embossedName: Optional[Any]
    minPaymentAmount: Optional[Any]
    cardStatusDetail: Optional[Any]
    contractStatusName: Optional[Any]
    regNumber: Optional[Any]
    isConfirm: Optional[str]
    isSourceDebit: Optional[Any]
    cardNumber: Optional[Any]
    packIncActive: Optional[Any]
    plasticStatus: Optional[Any]
    productStatus: Optional[Any]
    contractStatusCode: Optional[Any]
    approvalStatus: Optional[Any]
    cardCode: Optional[Any]
    cardClassDetail: Optional[Any]
    isExtendValid: Optional[Any]
    paidAmount: Optional[Any]
    currentMinPayment: Optional[Any]
    currentPayment: Optional[Any]
    debtMoment: Optional[Any]
    totalDebitAmount: Optional[Any]
    printingStatus: Optional[Any]
    cardProgramCd: Optional[Any]
    debitMethod: Optional[Any]
    cardOpenDate: Optional[Any]
    printAddress: Optional[Any]
    printDt: Optional[Any]
    channel: Optional[Any]
    htnt: Optional[Any]
    addtionalCard: Optional[Any]
    rbsNumber: Optional[Any]
    typeTemplate: Optional[Any]
    tokenStatus: Optional[Any]
    tokenCode: Optional[Any]
    serialId: Optional[Any]


class MenuModel(BaseModel):
    """Model representing a menu item in the user's interface."""

    code: Optional[str]
    name: Optional[str]
    parentCode: Optional[str]
    priority: Optional[str]
    menuType: Optional[str]
    icon: Optional[str]
    url: Optional[str]


class MenuManagerModel(BaseModel):
    """Model representing menu manager configuration."""

    code: Optional[str]
    version: Optional[str]
    isActive: Optional[str]
    maintenanceStartTime: Optional[Any]
    maintenanceEndTime: Optional[Any]


class SoftTokenModel(BaseModel):
    """Model representing a soft token device for authentication."""

    deviceNo: Optional[str]
    custId: Optional[str]
    deviceType: Optional[str]
    isDefault: Optional[str]
    clazz: Optional[str]
    isReset: Optional[Any]
    isMtAssigned: Optional[Any]
    deviceId: Optional[str]
    token: Optional[str]
    status: Optional[str]
    retry: Optional[int]
    mobileDeviceId: Optional[str]
    phoneId: Optional[str]
    assignedDt: Optional[Any]
    registeredDt: Optional[int]
    userId: Optional[Any]
    activedOtp: Optional[Any]
    smsCount: Optional[Any]
    hashUserId: Optional[Any]
    bioId: Optional[Any]
    bioLevel: Optional[Any]
    dotpPin: Optional[Any]
    pinUpdateDate: Optional[str]
    hashDeviceNo: Optional[Any]
    hashCifId: Optional[str]
    finalHashbankUID: Optional[Any]


class BiometricAuthDeviceModel(BaseModel):
    """Model representing a biometric authentication device."""

    deviceNo: Optional[str]
    custId: Optional[str]
    deviceType: Optional[str]
    isDefault: Optional[str]
    clazz: Optional[str]
    isReset: Optional[Any]
    isMtAssigned: Optional[Any]
    deviceId: Optional[str]
    token: Optional[Any]
    status: Optional[str]
    retry: Optional[int]
    mobileDeviceId: Optional[Any]
    phoneId: Optional[Any]
    assignedDt: Optional[Any]
    registeredDt: Optional[int]
    userId: Optional[Any]
    activedOtp: Optional[Any]
    smsCount: Optional[Any]
    hashUserId: Optional[str]
    bioId: Optional[str]
    bioLevel: Optional[str]
    dotpPin: Optional[Any]
    pinUpdateDate: Optional[str]
    hashDeviceNo: Optional[Any]
    hashCifId: Optional[str]
    finalHashbankUID: Optional[str]


class SectorDetailModel(BaseModel):
    """Model representing sector details for the customer."""

    Priority_Sector: Optional[str] = Field(None, alias="Priority Sector")
    Private_sector: Optional[str] = Field(None, alias="Private sector")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore"
    }


class CustModel(BaseModel):
    """Model representing the main customer information and nested data."""

    id: Optional[str]
    addr1: Optional[str]
    addr2: Optional[str]
    chrgAcctCd: Optional[str]
    cityCd: Optional[Any]
    correspondentEmail: Optional[str]
    createdBy: Optional[str]
    creditFrameworkBranch: Optional[Any]
    creditFrameworkContract: Optional[Any]
    custSectorCd: Optional[str]
    email1: Optional[str]
    entrustId: Optional[str]
    hndlingOfficerCd: Optional[str]
    hostCifId: Optional[str]
    idTypDt: Optional[int]
    idTypNo: Optional[str]
    idTypPlace: Optional[str]
    isDelete: Optional[str]
    isInactive: Optional[str]
    isLoan: Optional[str]
    mobilePhoneNo1: Optional[str]
    mobilePhoneNo2: Optional[Any]
    dob: Optional[str]
    dobObj: Optional[int]
    nm: Optional[str]
    orgUnitCd: Optional[str]
    phoneNo: Optional[str]
    secHndlingOfficerCd: Optional[str]
    spiUsrCd: Optional[str]
    srvcPcCd: Optional[str]
    stateCd: Optional[Any]
    userId: Optional[str]
    state: Optional[int]
    gender: Optional[str]
    password: Optional[str]
    imUserStatus: Optional[str]
    auth_type: Optional[Any]
    device_no: Optional[Any]
    chargeCd: Optional[Any]
    menuCd: Optional[Any]
    limitCd: Optional[Any]
    acct_list: Optional[Dict[str, UserInfoAccountModel]]
    cardList: Optional[Dict[str, UserInfoCardModel]]
    saving_acct_list: Optional[Dict[str, UserInfoAccountModel]]
    photoStr: Optional[Any]
    maxInactiveInterval: Optional[str]
    menuList: Optional[List[MenuModel]]
    lastLogin: Optional[str]
    ctryCd: Optional[str]
    refNumber: Optional[Any]
    createdDt: Optional[int]
    isSoftToken: Optional[str]
    softTokenList: Optional[List[SoftTokenModel]]
    deviceId: Optional[str]
    authDevice: Optional[Any]
    isMBCust: Optional[str]
    promotionUserList: Optional[List[Any]]
    isAcceptDigitalOTP: Optional[str]
    sectorDetail: Optional[SectorDetailModel]
    isOnlineSector: Optional[str]
    smsCount: Optional[Any]
    idTypType: Optional[str]
    corpBook: Optional[str]
    isNeedUpdateLimit: Optional[Any]
    idExpiryDate: Optional[int]
    biomatricAuthDeviceList: Optional[List[BiometricAuthDeviceModel]]
    inactiveReason: Optional[Any]
    defaultAccount: Optional[UserInfoAccountModel]
    email2: Optional[Any]
    passportExpDate: Optional[Any]
    featureInfo: Optional[Dict[str, Any]]
    requestId: Optional[Any]
    addr3: Optional[Any]
    rcfromState: Optional[str]
    kyc: Optional[Any]
    idTypDtValue: Optional[Any]


class InterfaceTypeModel(BaseModel):
    """Model representing the interface type information."""

    code: Optional[str]
    name: Optional[str]


class UserInfoResponseModal(BaseResponseModal):
    """Response model for user information, including customer, accounts, cards, and settings."""

    sessionId: Optional[str]
    cust: Optional[CustModel]
    menuManager: Optional[List[MenuManagerModel]]
    interfaceType: Optional[InterfaceTypeModel]
    maskingPhone: Optional[Any]
    listPhoneId: Optional[Any]
    existPin: Optional[Any]
    flagLoginSms: Optional[Any]
    webSecurityToken: Optional[Any]
