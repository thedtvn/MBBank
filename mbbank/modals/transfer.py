from .base import BaseResponseModal
from pydantic import BaseModel
from typing import Any, List


class AddInfo(BaseModel):
    """Nested additional info for transfer verification."""

    authenType: str
    authenTypeFinal: str


class TransferResponseModal(BaseResponseModal):
    """Model for transfer response."""

    srcAccountNumber: str
    srcAccountCurrency: str
    srcAccountType: str
    srcAccountName: str
    srcAccountAlias: str
    benAccountNumber: str
    benAccountName: str
    benBankName: Any = None
    benBankCd: str
    amount: str
    message: str
    chargeCode: str
    fee: str
    transferType: str
    ftId: Any = None
    vat: str
    totalFee: str
    authenType: str
    addInfo: AddInfo
    riskCode: Any = None
    riskMessage: Any = None
    beanResponse: Any = None
    posMid: Any = None


class AuthListItem(BaseModel):
    """
    Single auth item in authList.
    """

    code: str
    name: str
    alias: str


class AuthTransferResponseModal(BaseResponseModal):
    """
    Model for authenticating transfer message response.
    """

    authList: List[AuthListItem]


# Yes somehow this obj has refNo
class TransactionAuthen(BaseResponseModal):
    """
    Model representing the `transactionAuthen` object in the transaction authentication response.
    """

    id: str
    custId: str
    sourceAccount: str
    destAccount: str
    amount: str
    transactionType: str
    isVerified: Any = None
    destAccountName: str
    deviceId: Any = None
    authenType: Any = None
    extTransactionId: Any = None
    sessionId: Any = None
    bioId: Any = None
    hostCifId: Any = None
    idTypNo: Any = None
    hashbankUidCif: Any = None
    isMatchHashbankId: Any = None


class TransactionAuthenResponseModal(BaseResponseModal):
    """
    Model for transaction authentication response.
    """

    transactionAuthen: TransactionAuthen
