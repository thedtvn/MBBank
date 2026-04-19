import datetime
import typing

if typing.TYPE_CHECKING:
    from mbbank.sync import MBBank

from mbbank.base import TransferContextBase
from mbbank.errors import (
    BankNotFoundError,
    MBBankError,
)
from mbbank.modals import (
    AuthListItem,
    AuthTransferResponseModal,
    Bank,
    TransactionAuthenResponseModal,
    TransferResponseModal,
)


class TransferContext(TransferContextBase):
    """
    Transfer context manager for account to account transfer

    Attributes:
        to_account_name (AccountNameResponseModal or None): destination account name info, this available when call makeTransferAccountToAccount
        refNo (str or None): reference number
        timestamp (int or None): timestamp
        transaction_authen (TransactionAuthenResponseModal or None): transaction authentication info
        mbbank (MBBank): MBBank instance
        src_account (str): source account number
        dest_account (str): destination account number
        bank_code (str): bank code of the destination account
        amount (int): amount to transfer
        message (str): transfer message
    """

    mbbank: "MBBank"

    def __init__(
        self,
        mbbank_instance: "MBBank",
        *,
        src_account: str,
        dest_account: str,
        bank_code: str,
        amount: int,
        message: str,
    ):
        """
        Initialize transfer context

        Note: This for advance flow only, normal flow not need to call this class directly use makeTransferAccountToAccount instead.

        Args:
            mbbank_instance (MBBank): MBBank instance
            src_account (str): Source account number
            dest_account (str): Destination account number
            bank_code (str): Bank code of the destination account get from getBankList eg "MB".
            amount (int): Amount to transfer
            message (str): Transfer message
        """
        super().__init__(
            src_account=src_account,
            dest_account=dest_account,
            bank_code=bank_code,
            amount=amount,
            message=message,
        )
        self.mbbank = mbbank_instance

    def getBank(self) -> Bank:
        """
        Get transfer destination bank info

        Returns:
            success (Bank): bank info
        """
        if self.bank is not None:
            return self.bank
        bank_list = self.mbbank.getBankList()
        for bank in bank_list.listBank:
            if bank.bankCode == self.bank_code:
                self.bank = bank
                return bank
        raise BankNotFoundError("Bank code not found in bank list")

    def verify_transfer(self) -> TransferResponseModal:
        """
        Verify transfer info before making transfer

        Note: This for advance flow only, normal flow not need to call this method directly use get_qr_code instead

        Returns:
            success (TransferResponseModal): verify transfer response

        Raises:
            MBBankError: if start() not called before verify_transfer() to prepare bank and account name
            MBBankAPIError: if api response not ok
        """
        if self.bank is None or self.to_account_name is None:
            raise MBBankError(
                "Call start() before verify_transfer() to prepare bank and account name"
            )
        json_data = {
            "srcAccountNumber": self.src_account,
            "benAccountNumber": self.dest_account,
            "benAccountName": self.to_account_name.benName,
            "benBankCd": self.bank.bankCode,
            "amount": self.amount,
            "message": self.message,
            "transferType": self.bank.typeTransfer,
            "destType": "ACCOUNT",
            "otp": "",
        }
        data_out = self.mbbank._req(
            "https://online.mbbank.com.vn/api/retail_web/transfer/v1.0/verify-make-transfer",
            json=json_data,
            encrypt=True,
        )
        return TransferResponseModal.model_validate(data_out, strict=True)

    def get_auth_list(self) -> AuthTransferResponseModal:
        """
        Get authentication method list for transfer

        Returns:
            success (AuthTransferResponseModal): authentication method list

        Raises:
            MBBankAPIError: if api response not ok
            BankNotFoundError: if bank code not found in bank list
        """
        if self.bank is None:
            self.bank = self.getBank()
        json_data = {
            "sourceAccount": self.src_account,
            "amount": self.amount,
            "serviceCode": f"GCM_FTR_DOM_{self.bank.typeTransfer}",
        }
        data_out = self.mbbank._req(
            "https://online.mbbank.com.vn/api/retail_web/internetbanking/getAuthList",
            json=json_data,
            encrypt=True,
        )
        return AuthTransferResponseModal.model_validate(data_out, strict=True)

    def create_transaction_authen(self) -> TransactionAuthenResponseModal:
        """
        Create transaction authentication payload

        Note: This for advance flow only, normal flow not need to call this method directly use get_qr_code instead

        Returns:
            success (TransactionAuthenResponseModal): transaction authentication response

        Raises:
            MBBankAPIError: if api response not ok
        """
        if self.to_account_name is None or self.bank is None:
            raise MBBankError(
                "Call start() before create_transaction_authen() to prepare account name"
            )
        self.refNo = f"{self.mbbank._userid}-{self.mbbank._get_now_time()}"
        custId = self.mbbank.userinfo().cust.id
        json_data = {
            "transactionAuthen": {
                "refNo": self.refNo,
                "custId": custId,
                "sourceAccount": self.src_account,
                "destAccount": self.dest_account,
                "amount": self.amount,
                "transactionType": f"GCM_FTR_DOM_{self.bank.typeTransfer}",
                "destAccountName": self.to_account_name.benName,
            }
        }
        data_out = self.mbbank._req(
            "https://online.mbbank.com.vn/api/retail_web/vtap/createTransactionAuthen",
            json=json_data,
            encrypt=True,
        )
        return TransactionAuthenResponseModal.model_validate(data_out, strict=True)

    def transfer(self, otp: str, auth_type: AuthListItem) -> TransferResponseModal:
        """
        Execute transfer with provided OTP

        Args:
            otp (str): OTP code from authentication method
            auth_type (AuthListItem): authentication method get from get_auth_list()

        Returns:
            success (TransferResponseModal): transfer response

        Raises:
            MBBankError: if get_qr_code() not called before transfer()
            MBBankAPIError: if api response not ok
        """
        if self.transaction_authen is None or self.timestamp is None:
            raise MBBankError(
                "Call get_qr_code() before transfer() to prepare authentication"
            )
        elif self.bank is None or self.to_account_name is None:
            raise MBBankError(
                "Call start() before transfer() to prepare bank and account name"
            )
        otp_crafted = self._craft_otp(otp, auth_type)
        json_data = {
            "srcAccountNumber": self.src_account,
            "benAccountNumber": self.dest_account,
            "benAccountName": self.to_account_name.benName,
            "benBankCd": self.bank.bankCode,
            "message": self.message,
            "transferType": self.bank.typeTransfer,
            "destType": "ACCOUNT",
            "amount": self.amount,
            "otp": otp_crafted,
        }
        data_out = self.mbbank._req(
            "https://online.mbbank.com.vn/api/retail_web/transfer/v1.0/make-transfer",
            json=json_data,
            encrypt=True,
        )
        return TransferResponseModal.model_validate(data_out, strict=True)

    def get_qr_code(self) -> str:
        """
        Get QR code string for authentication

        Returns:
            success (str): QR code content string

        Raises:
            MBBankError: if start() not called before get_qr_code() to prepare
            MBBankAPIError: if api response not ok
        """
        self.timestamp = int(datetime.datetime.now().timestamp())
        self.transaction_authen = self.create_transaction_authen().transactionAuthen
        return f"TRANID|{self.transaction_authen.id}"

    def start(self) -> "TransferContext":
        """
        Start transfer process this will verify transfer info and prepare for authentication

        Note: This for advance flow only, normal flow not need to call this method directly use makeTransferAccountToAccount instead.

        Returns:
            success (TransferContext): self instance for chaining

        Raises:
            MBBankAPIError: if api response not ok
        """
        bank = self.getBank()
        self.to_account_name = self.mbbank.getAccountName(
            accountNo=self.dest_account,
            bankCode=bank.bankCode,
            debitAccount=self.src_account,
        )
        self.verify_transfer()
        return self
