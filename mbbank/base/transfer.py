import typing

from mbbank.errors import MBBankError
from mbbank.modals import (
    AccountNameResponseModal,
    AccountTransfer,
    AuthListItem,
    Bank,
    TransactionAuthen,
)


class BaseTransferContext:
    """
    Base transfer context with shared attributes and utility methods for all transfer types.

    Attributes:
        mbbank: MBBank instance (sync or async)
        src_account (str): source account number
        refNo (str or None): reference number
        timestamp (int or None): timestamp
        transaction_authen (TransactionAuthen or None): transaction authentication info
    """

    mbbank: typing.Any  # Can be MBBank or MBBankAsync
    src_account: str
    refNo: typing.Optional[str]
    timestamp: typing.Optional[int]
    transaction_authen: typing.Optional[TransactionAuthen]

    def __init__(self, *, src_account: str):
        """
        Initialize base transfer context

        Args:
            src_account (str): Source account number
        """
        self.src_account = src_account
        self.refNo = None
        self.timestamp = None
        self.transaction_authen = None

    def _craft_otp(self, otp: str, auth_type: AuthListItem) -> str:
        """
        Craft OTP string for transfer authentication

        Args:
            otp (str): OTP code from authentication method
            auth_type (AuthListItem): authentication method

        Returns:
            str: Crafted OTP string

        Raises:
            MBBankError: if get_qr_code() not called before _craft_otp()
        """
        if self.timestamp is None or self.refNo is None or self.transaction_authen is None:
            raise MBBankError("Call get_qr_code() before _craft_otp() to prepare authentication")
        return f"ibr|{auth_type.code}||{otp}||{self.timestamp}|{self.transaction_authen.id}|{self.refNo}"


class TransferContextBase(BaseTransferContext):
    """
    Base transfer context for single account to account transfer.

    Attributes:
        to_account_name (AccountNameResponseModal or None): destination account name info
        dest_account (str): destination account number
        bank_code (str): bank code of the destination account
        amount (int): amount to transfer
        message (str): transfer message
        bank (Bank or None): destination bank info
    """

    to_account_name: typing.Optional[AccountNameResponseModal]
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
        super().__init__(src_account=src_account)
        self.to_account_name = None
        self.dest_account = dest_account
        self.bank_code = bank_code
        self.amount = amount
        self.message = message
        self.bank = None


class BulkTransferContextBase(BaseTransferContext):
    """
    Base transfer context for bulk transfer (account to many accounts).

    Attributes:
        dest_accounts (list[AccountTransfer]): list of destination account info for bulk transfer
        description (str): description for the bulk transfer
        amount (Optional[str]): total amount (set after verify_transfer)
        filename (str): file name for the bulk transfer excel file, default "Chuyenkhoantheobangke.xlsx"
    """

    dest_accounts: list[AccountTransfer]
    description: str
    amount: typing.Optional[str]

    def __init__(
        self,
        *,
        src_account: str,
        dest_accounts: list[AccountTransfer],
        description: str = "",
        bulk_file_name: str = "Chuyenkhoantheobangke.xlsx",
    ):
        """
        Initialize bulk transfer context base

        Args:
            src_account (str): Source account number
            dest_accounts (list[AccountTransfer]): list of destination account info for bulk transfer
            description (str): description for the transfer
            filename (str): file name for the bulk transfer excel file, default "Chuyenkhoantheobangke.xlsx"
        """
        super().__init__(src_account=src_account)
        self.dest_accounts = dest_accounts
        self.description = description
        self.amount = None
        self.filename = bulk_file_name
