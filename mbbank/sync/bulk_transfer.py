import datetime
import typing

if typing.TYPE_CHECKING:
    from mbbank.sync import MBBank

from mbbank.base import BulkTransferContextBase
from mbbank.errors import (
    BankNotFoundError,
    MBBankError,
)
from mbbank.modals import (
    AccountTransfer,
    AuthListItem,
    AuthTransferResponseModal,
    Bank,
    BulkTransferResponseModal,
    TransactionAuthenResponseModal,
)


class BulkTransferContext(BulkTransferContextBase):
    """
    Bulk Transfer context manager for account to many account transfer

    Attributes:
        mbbank (MBBank): MBBank instance
        src_account (str): source account number
        dest_accounts (list[AccountTransfer]): list of destination account info for bulk transfer
        description (str): description for the bulk transfer
        amount (str or None): total amount (set after verify_transfer)
        refNo (str or None): reference number
        timestamp (int or None): timestamp
        transaction_authen (TransactionAuthen or None): transaction authentication info
        filename (str): file name for the bulk transfer excel file, default "Chuyenkhoantheobangke.xlsx"
    """

    mbbank: "MBBank"

    def __init__(
        self,
        mbbank_instance: "MBBank",
        *,
        src_account: str,
        dest_accounts: list[AccountTransfer],
        description: str = "",
        bulk_file_name: str = "Chuyenkhoantheobangke.xlsx",
    ):
        """
        Initialize bulk transfer context

        Note: This for advance flow only, normal flow not need to call this class directly use makeBulkTransfer instead.

        Args:
            mbbank_instance (MBBank): MBBank instance
            src_account (str): Source account number
            dest_accounts (list[AccountTransfer]): list of destination account info for bulk transfer
            description (str): description for the transfer, this will be the description of the bulk transfer
            bulk_file_name (str): bulk file name for the transfer file, this will log into bulk transfer detail, default to "Chuyenkhoantheobangke.xlsx"
        """
        super().__init__(
            src_account=src_account,
            dest_accounts=dest_accounts,
            description=description,
            bulk_file_name=bulk_file_name,
        )
        self.mbbank = mbbank_instance

    def getBank(self, account: AccountTransfer) -> Bank:
        """
        Get transfer destination bank info

        Args:
            account (AccountTransfer): destination account info

        Returns:
            success (Bank): bank info

        Raises:
            BankNotFoundError: if bank code not found in bank list
        """
        bank_list = self.mbbank.getBankList()
        for bank in bank_list.listBank:
            if bank.smlCode == account.benBankCode:
                return bank
        raise BankNotFoundError("Bank code not found in bank list")

    def verify_transfer(self) -> BulkTransferResponseModal:
        """
        Verify transfer info before making transfer

        Note: This for advance flow only, normal flow not needs to call this method directly use get_qr_code instead

        Returns:
            success (BulkTransferResponseModal): verify transfer response

        Raises:
            MBBankAPIError: if api response not ok
        """
        json_data = {
            "bulkpaymentList": [model.model_dump() for model in self.dest_accounts],
            "description": self.description,
            "sourceNumber": self.src_account,
        }
        data_out = self.mbbank._req(
            "https://online.mbbank.com.vn/api/retail-bulkpaymentms/v1.0/verify-bulk-payment",
            json=json_data,
            encrypt=True,
        )
        return BulkTransferResponseModal.model_validate(data_out, strict=True)

    def get_auth_list(self) -> AuthTransferResponseModal:
        """
        Get authentication method list for transfer

        Returns:
            success (AuthTransferResponseModal): authentication method list

        Raises:
            MBBankError: if start() not called before get_auth_list()
            MBBankAPIError: if api response not ok
        """
        if self.amount is None:
            raise MBBankError("Call start() before get_auth_list() to prepare bank and account name")

        json_data = {
            "sourceAccount": self.src_account,
            "amount": self.amount,
            "serviceCode": "BULK_TRANSFER",
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
            MBBankError: if start() not called before create_transaction_authen()
            MBBankAPIError: if api response not ok
        """
        if self.amount is None:
            raise MBBankError("Call start() before create_transaction_authen() to prepare account name")
        self.refNo = f"{self.mbbank._userid}-{self.mbbank._get_now_time()}"
        custId = self.mbbank.userinfo().cust.id
        json_data = {
            "transactionAuthen": {
                "refNo": self.refNo,
                "custId": custId,
                "sourceAccount": self.src_account,
                "destAccount": "",
                "amount": self.amount,
                "transactionType": "BULK_TRANSFER",
                "destAccountName": "",
            }
        }
        data_out = self.mbbank._req(
            "https://online.mbbank.com.vn/api/retail_web/vtap/createTransactionAuthen",
            json=json_data,
            encrypt=True,
        )
        return TransactionAuthenResponseModal.model_validate(data_out, strict=True)

    def transfer(self, otp: str, auth_type: AuthListItem) -> BulkTransferResponseModal:
        """
        Execute transfer with provided OTP

        Args:
            otp (str): OTP code from authentication method
            auth_type (AuthListItem): authentication method get from get_auth_list()

        Returns:
            success (BulkTransferResponseModal): transfer response

        Raises:
            MBBankError: if get_qr_code() not called before transfer()
            MBBankAPIError: if api response not ok
        """
        if self.transaction_authen is None or self.timestamp is None:
            raise MBBankError("Call get_qr_code() before transfer() to prepare authentication")
        if self.amount is None:
            raise MBBankError("Call start() before transfer() to prepare bank and account name")
        otp_crafted = self._craft_otp(otp, auth_type)
        json_data = {
            "bulkpaymentList": [model.model_dump() for model in self.dest_accounts],
            "description": self.description,
            "sourceNumber": self.src_account,
            "bulkFileName": self.filename,
            "otp": otp_crafted,
        }
        data_out = self.mbbank._req(
            "https://online.mbbank.com.vn/api/retail-bulkpaymentms/v1.0/make-bulk-payment",
            json=json_data,
            encrypt=True,
        )
        return BulkTransferResponseModal.model_validate(data_out, strict=True)

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

    def start(self) -> "BulkTransferContext":
        """
        Start transfer process this will verify transfer info and prepare for authentication

        Note: This for advance flow only, normal flow not need to call this method directly use makeBulkTransfer instead.

        Returns:
            success (BulkTransferContext): self instance for chaining

        Raises:
            MBBankAPIError: if api response not ok
        """
        for transfer in self.dest_accounts:
            if transfer.customerName is not None:
                continue

            transfer.customerName = self.mbbank.getAccountName(
                transfer.creditAccount, self.getBank(transfer).bankCode, self.src_account
            ).benName

        self.amount = self.verify_transfer().totalAmount
        return self
