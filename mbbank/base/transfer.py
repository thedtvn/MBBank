import typing

from mbbank.errors import MBBankError
from mbbank.modals import (
    AccountNameResponseModal,
    AuthListItem,
    Bank,
    TransactionAuthen,
)


class TransferContextBase:
    """
    Base transfer context with shared attributes and utility methods for account to account transfer.

    Attributes:
        to_account_name (AccountNameResponseModal or None): destination account name info
        refNo (str or None): reference number
        timestamp (int or None): timestamp
        transaction_authen (TransactionAuthen or None): transaction authentication info
        src_account (str): source account number
        dest_account (str): destination account number
        bank_code (str): bank code of the destination account
        amount (int): amount to transfer
        message (str): transfer message
        bank (Bank or None): destination bank info
    """

    to_account_name: typing.Optional[AccountNameResponseModal]
    refNo: typing.Optional[str]
    timestamp: typing.Optional[int]
    transaction_authen: typing.Optional[TransactionAuthen]
    src_account: str
    dest_account: str
    bank_code: str
    amount: int
    message: str
    bank: typing.Optional[Bank]

    def __init__(
        self,
        *,
        src_account: str,
        dest_account: str,
        bank_code: str,
        amount: int,
        message: str,
    ):
        """
        Initialize transfer context base

        Args:
            src_account (str): Source account number
            dest_account (str): Destination account number
            bank_code (str): Bank code of the destination account get from getBankList eg "MB".
            amount (int): Amount to transfer
            message (str): Transfer message
        """
        self.to_account_name = None
        self.refNo = None
        self.timestamp = None
        self.transaction_authen = None
        self.src_account = src_account
        self.dest_account = dest_account
        self.bank_code = bank_code
        self.amount = amount
        self.message = message
        self.bank = None

    def _craft_otp(self, otp: str, auth_type: AuthListItem) -> str:
        if (
            self.timestamp is None
            or self.refNo is None
            or self.transaction_authen is None
        ):
            raise MBBankError(
                "Call get_qr_code() before _craft_otp() to prepare authentication"
            )
        return f"ibr|{auth_type.code}||{otp}||{self.timestamp}|{self.transaction_authen.id}|{self.refNo}"
