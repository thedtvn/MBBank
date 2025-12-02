import datetime
import base64
import hashlib
import typing
import requests
from .capcha_ocr import CapchaOCR, CapchaProcessing
from .wasm_helper import wasm_encrypt
from .modals import (
    BalanceResponseModal,
    BalanceLoyaltyResponseModal,
    BankListResponseModal,
    BeneficiaryListResponseModal,
    CardListResponseModal,
    AccountByPhoneResponseModal,
    UserInfoResponseModal,
    LoanListResponseModal,
    SavingListResponseModal,
    InterestRateResponseModal,
    TransactionHistoryResponseModal,
    CardTransactionsResponseModal,
    SavingDetailResponseModal,
    SavedBeneficiaryListResponseModal,
    AccountNameResponseModal,
    ServiceTokenResponseModal,
    ATMCardIDResponseModal,
    ATMAccountNameResponseModal,
    Bank,
    TransferResponseModal,
    AuthTransferResponseModal,
    TransactionAuthenResponseModal,
    AuthListItem,
)
from .errors import CapchaError, MBBankAPIError, BankNotFoundError, MBBankError

headers_default = {
    "Cache-Control": "max-age=0",
    "Accept": "application/json, text/plain, */*",
    "Authorization": "Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Origin": "https://online.mbbank.com.vn",
    "Referer": "https://online.mbbank.com.vn/pl/login?returnUrl=%2F",
    "App": "MB_WEB",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


class MBBank:
    """Core class

    Attributes:
        deviceIdCommon (str): Device id common
        sessionId (str or None): Current Session id

    Args:
        username (str): MBBank Account Username
        password (str): MBBank Account Password
        proxy (str, optional): Proxy url. Example: "http://127.0.0.1:8080". Defaults to None.
        ocr_class (CapchaProcessing, optional): instance of CapchaProcessing class. Defaults to CapchaOCR().
        retry_times (int, optional): number of retry times for capcha processing. Defaults to 30 ( worst case ).
        timeout (Union[float, Tuple[float, float]], optional): request timeout in seconds or (connect timeout, read timeout) or None for no timeout. Defaults to None.
    """

    FPR = "c7a1beebb9400375bb187daa33de9659"

    def __init__(
        self,
        *,
        username: str,
        password: str,
        proxy: typing.Optional[str] = None,
        ocr_class: typing.Optional[CapchaProcessing] = None,
        retry_times: int = 30,
        timeout: typing.Union[float, typing.Tuple[float, float], None] = None,
    ):
        self._userid = username
        self._password = password
        self._wasm_cache = None
        if proxy is not None:
            proxy_protocol = proxy.split("://")[0]
            self.proxy = {proxy_protocol: proxy}
        else:
            self.proxy = {}
        self.ocr_class = CapchaOCR()
        if ocr_class is not None:
            if not isinstance(ocr_class, CapchaProcessing):
                raise ValueError("ocr_class must be instance of CapchaProcessing")
            self.ocr_class = ocr_class
        self.sessionId = None
        self._userinfo = None
        self._temp = {}
        self.deviceIdCommon = f"abi2jojr-mbib-0000-0000-{self._get_now_time()}"
        self.retry_times = retry_times
        self.timeout = timeout

    def _get_now_time(self):
        now = datetime.datetime.now()
        microsecond = int(now.strftime("%f")[:2])
        return now.strftime(f"%Y%m%d%H%M{microsecond}")

    def _req(self, url, *, json=None, headers=None, encrypt: bool = False) -> dict:
        if headers is None:
            headers = {}
        if json is None:
            json = {}
        while True:
            if self.sessionId is None:
                self._authenticate()
            rid = f"{self._userid}-{self._get_now_time()}"
            json_data = {
                "sessionId": self.sessionId if self.sessionId is not None else "",
                "refNo": rid,
                "deviceIdCommon": self.deviceIdCommon,
            }
            json_data.update(json)
            headers.update(headers_default)
            headers["X-Request-Id"] = rid
            headers["RefNo"] = rid
            headers["DeviceId"] = self.deviceIdCommon
            if encrypt:
                wasm_bytes = self._get_wasm_file()
                data_encrypt = wasm_encrypt(wasm_bytes, json_data)
                json_data = {"dataEnc": data_encrypt}
            with requests.post(
                url, headers=headers, json=json_data, proxies=self.proxy
            ) as r:
                data_out = r.json()
            if data_out["result"] is None:
                self.getBalance()
            elif data_out["result"]["ok"]:
                data_out.pop("result", None)
                break
            elif data_out["result"]["responseCode"] == "GW200":
                self._authenticate()
            else:
                raise MBBankAPIError(data_out["result"])
        return data_out

    def _get_wasm_file(self):
        if self._wasm_cache is not None:
            return self._wasm_cache
        file_data = requests.get(
            "https://online.mbbank.com.vn/assets/wasm/main.wasm",
            proxies=self.proxy,
            timeout=self.timeout,
        ).content
        self._wasm_cache = file_data
        return file_data

    def get_capcha_image(self) -> bytes:
        """
        Get capcha image as bytes

        Returns:
            success (bytes): capcha image as bytes
        """
        rid = f"{self._userid}-{self._get_now_time()}"
        json_data = {
            "sessionId": "",
            "refNo": rid,
            "deviceIdCommon": self.deviceIdCommon,
        }
        headers = headers_default.copy()
        headers["X-Request-Id"] = rid
        headers["Deviceid"] = self.deviceIdCommon
        headers["Refno"] = rid
        with requests.post(
            "https://online.mbbank.com.vn/api/retail-internetbankingms/getCaptchaImage",
            headers=headers,
            json=json_data,
            proxies=self.proxy,
            timeout=self.timeout,
        ) as r:
            data_out = r.json()
            return base64.b64decode(data_out["imageString"])

    def login(self, captcha_text: str):
        """
        Login to MBBank account

        Args:
            captcha_text (str): capcha text from capcha image

        Raises:
            MBBankAPIError: if login failed
        """
        payload = {
            "userId": self._userid,
            "password": hashlib.md5(self._password.encode()).hexdigest(),
            "captcha": captcha_text,
            "sessionId": "",
            "refNo": f"{self._userid}-{self._get_now_time()}",
            "deviceIdCommon": self.deviceIdCommon,
            "ibAuthen2faString": self.FPR,
        }
        wasm_bytes = self._get_wasm_file()
        data_encrypt = wasm_encrypt(wasm_bytes, payload)
        with requests.post(
            "https://online.mbbank.com.vn/api/retail_web/internetbanking/v2.0/doLogin",
            headers=headers_default,
            json={"dataEnc": data_encrypt},
            proxies=self.proxy,
            timeout=self.timeout,
        ) as r:
            data_out = r.json()
        if data_out["result"]["ok"]:
            self.sessionId = data_out["sessionId"]
            data_out.pop("result", None)
            self._userinfo = data_out
            self._verify_biometric_check()
            return
        else:
            raise MBBankAPIError(data_out["result"])

    def getServiceToken(self) -> ServiceTokenResponseModal:
        """
        Get service token for external service usage

        Returns:
            success (ServiceTokenResponseModal): service token
        """
        if self._userinfo is None:
            self._authenticate()
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/common/getServiceToken"
        )
        return ServiceTokenResponseModal.model_validate(data_out, strict=True)

    def _authenticate(self):
        try_count = 0
        while try_count < self.retry_times:
            try_count += 1
            self._userinfo = None
            self.sessionId = None
            img_bytes = self.get_capcha_image()
            captcha_text = self.ocr_class.process_image(img_bytes)
            try:
                return self.login(captcha_text)
            except MBBankAPIError as e:
                if e.code == "GW283":
                    continue  # capcha error, try again
                raise e
        raise CapchaError(
            f"Exceeded maximum retry times for capcha processing ({self.retry_times})"
        )

    def _verify_biometric_check(self):
        self._req(
            "https://online.mbbank.com.vn/api/retail-go-ekycms/v1.0/verify-biometric-nfc-transaction"
        )

    def getTransactionAccountHistory(
        self,
        *,
        accountNo: typing.Optional[str] = None,
        from_date: datetime.datetime,
        to_date: datetime.datetime,
    ) -> TransactionHistoryResponseModal:
        """
        Get account transaction history

        Args:
            accountNo (str, optional): Sub account number Defaults to Main Account number.
            from_date (datetime.datetime): transaction from date
            to_date (datetime.datetime): transaction to date

        Returns:
            success (TransactionHistoryResponseModal): account transaction history

        Raises:
            MBBankAPIError: if api response not ok
        """
        if self._userinfo is None:
            self._authenticate()
        json_data = {
            "accountNo": self._userid if accountNo is None else accountNo,
            "fromDate": from_date.strftime("%d/%m/%Y"),
            "toDate": to_date.strftime("%d/%m/%Y"),  # max 3 months
        }
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail-transactionms/transactionms/get-account-transaction-history",
            json=json_data,
        )
        return TransactionHistoryResponseModal.model_validate(data_out, strict=True)

    def getBalance(self) -> BalanceResponseModal:
        """
        Get all main account and subaccount balance

        Returns:
            success (BalanceResponseModal): balance model

        Raises:
            MBBankAPIError: if api response not ok
        """
        if self._userinfo is None:
            self._authenticate()
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail-accountms/accountms/getBalance"
        )
        return BalanceResponseModal.model_validate(data_out, strict=True)

    def getBalanceLoyalty(self) -> BalanceLoyaltyResponseModal:
        """
        Get Account loyalty rank and Member loyalty point

        Returns:
            success (BalanceLoyaltyResponseModal): loyalty balance model

        Raises:
            MBBankAPIError: if api response not ok
        """
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/loyalty/getBalanceLoyalty"
        )
        return BalanceLoyaltyResponseModal.model_validate(data_out, strict=True)

    def getInterestRate(self, currency: str = "VND") -> InterestRateResponseModal:
        """
        Get saving interest rate

        Args:
            currency (str, optional): currency ISO 4217 format. Defaults to "VND" (Vietnam Dong).

        Returns:
            success (InterestRateResponseModal): interest rate

        Raises:
            MBBankAPIError: if api response not ok
        """
        json_data = {
            "productCode": "TIENGUI.KHN.EMB",
            "currency": currency,
        }
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/saving/getInterestRate",
            json=json_data,
        )
        return InterestRateResponseModal.model_validate(data_out, strict=True)

    def getFavorBeneficiaryList(
        self,
        *,
        transactionType: typing.Literal["TRANSFER", "PAYMENT"],
        searchType: typing.Literal["MOST", "LATEST"],
    ) -> BeneficiaryListResponseModal:
        """
        Get all favor or most transfer beneficiary list from your account

        Args:
            transactionType (Literal["TRANSFER", "PAYMENT"]): transaction type
            searchType (Literal["MOST", "LATEST"]): search type

        Returns:
            success (BeneficiaryListResponseModal): favor beneficiary list

        Raises:
            MBBankAPIError: if api response not ok
        """
        json_data = {"transactionType": transactionType, "searchType": searchType}
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/internetbanking/getFavorBeneficiaryList",
            json=json_data,
        )
        return BeneficiaryListResponseModal.model_validate(data_out, strict=True)

    def getCardList(self) -> CardListResponseModal:
        """
        Get all card list from your account

        Returns:
            success (CardListResponseModal): card list

        Raises:
            MBBankAPIError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/card/getList")
        return CardListResponseModal.model_validate(data_out, strict=True)

    def getSavingList(self) -> SavingListResponseModal:
        """
        Get all saving list from your account

        Returns:
            success (SavingListResponseModal): saving list

        Raises:
            MBBankAPIError: if api response not ok
        """
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail-savingms/saving/v3.0/getList"
        )
        return SavingListResponseModal.model_validate(data_out, strict=True)

    def getSavingDetail(
        self, accNo: str, accType: typing.Literal["OSA", "SBA"]
    ) -> SavingDetailResponseModal:
        """
        Get saving detail by account number

        Args:
            accNo (str): saving account number
            accType (Literal["OSA", "SBA"]): saving account type | OSA: Online Saving Account, SBA: Saving Bank Account

        Returns:
            success (c): saving detail

        Raises:
            MBBankAPIError: if api response not ok
        """
        json_data = {"accNo": accNo, "accType": accType}
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/saving/getDetail",
            json=json_data,
        )
        return SavingDetailResponseModal.model_validate(data_out, strict=True)

    def getLoanList(self) -> LoanListResponseModal:
        """
        Get all loan list from your account

        Returns:
            success (LoanListResponseModal): loan list

        Raises:
            MBBankAPIError: if api response not ok
        """
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail-onlineloanms/loan/getList"
        )
        return LoanListResponseModal.model_validate(data_out, strict=True)

    def getCardTransactionHistory(
        self, cardNo: str, from_date: datetime.datetime, to_date: datetime.datetime
    ) -> CardTransactionsResponseModal:
        """
        Get card transaction history

        Args:
            cardNo (str): card number get from getCardList
            from_date (datetime.datetime): from date
            to_date (datetime.datetime): to date

        Returns:
            success (CardListResponseModal): card transaction history

        Raises:
            MBBankAPIError: if api response not ok
        """
        json_data = {
            "accountNo": cardNo,
            "fromDate": from_date.strftime("%d/%m/%Y"),
            "toDate": to_date.strftime("%d/%m/%Y"),  # max 3 months
            "historyNumber": "",
            "historyType": "DATE_RANGE",
            "type": "CARD",
        }
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/common/getTransactionHistory",
            json=json_data,
        )
        return CardTransactionsResponseModal.model_validate(data_out, strict=True)

    def getBankList(self) -> BankListResponseModal:
        """
        Get transfer all bank list

        Returns:
            success (BankListResponseModal): bank list

        Raises:
            MBBankAPIError: if api response not ok
        """
        if "bank_list" in self._temp:
            return BankListResponseModal.model_validate(
                self._temp["bank_list"], strict=True
            )  # use cache seen as bank list not change often
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/common/getBankList"
        )
        self._temp["bank_list"] = data_out
        return BankListResponseModal.model_validate(data_out, strict=True)

    def getAccountByPhone(self, phone: str) -> AccountByPhoneResponseModal:
        """
        Get transfer account info by phone (MBank internal account only)

        Args:
            phone (str): MBBank account phone number

        Returns:
            success (AccountByPhoneResponseModal): account info

        Raises:
            MBBankAPIError: if api response not ok
        """
        json_data = {"phone": phone}
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/common/getAccountByPhone",
            json=json_data,
        )
        return AccountByPhoneResponseModal.model_validate(data_out, strict=True)

    def getSavedBeneficiary(self) -> SavedBeneficiaryListResponseModal:
        """
        Get all saved beneficiary list from your account.

        Returns:
            success (SavedBeneficiaryListResponseModal): saved beneficiary list
        Raises:
            MBBankAPIError: if api response not ok
        """
        json_data = {"type": "TRANSFER"}
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/common/getBeneficiary",
            json=json_data,
        )
        return SavedBeneficiaryListResponseModal.model_validate(data_out, strict=True)

    def getAccountName(
        self, accountNo: str, bankCode: str, debitAccount: str
    ) -> AccountNameResponseModal:
        """
        Get account name by account number

        Args:
            accountNo (str): account number that you want to get name
            bankCode (str): bank code get from getBankList
            debitAccount (str): your account number to transfer from

        Returns:
            success (AccountNameResponseModal): account obj

        Raises:
            MBBankAPIError: if api response not ok
        """
        json_data = {
            "creditAccount": accountNo,
            "creditAccountType": "ACCOUNT",
            "bankCode": bankCode,
            "debitAccount": debitAccount,
            "remark": "",
        }
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/transfer/v1.0/inquiry-account-name",
            json=json_data,
        )
        return AccountNameResponseModal.model_validate(data_out, strict=True)

    def getATMCardID(self, cardNumber: str) -> ATMCardIDResponseModal:
        """
        Get ATM Card ID by card number

        Args:
            cardNumber (str): card number

        Returns:
            success (ATMCardIDResponseModal): ATM Card ID response

        Raises:
            MBBankAPIError: if api response not ok
        """
        service_token = self.getServiceToken()
        headers = headers_default.copy()
        headers["authorization"] = service_token.type + " " + service_token.token
        json_data = {
            "cardNumber": cardNumber,
            "requestID": f"{self._userid}-{self._get_now_time()}",
        }
        with requests.post(
            "https://mbcard.mbbank.com.vn:8446/mbcardgw/internet/cardinfo/v1_0/generateid",
            headers=headers,
            json=json_data,
            proxies=self.proxy,
            timeout=self.timeout,
        ) as r:
            data_out = r.json()
        return ATMCardIDResponseModal.model_validate(data_out, strict=True)

    def getATMAccountName(
        self, cardNumber: str, debitAccount: str
    ) -> ATMAccountNameResponseModal:
        """
        Get ATM Account Name by card number

        Args:
            cardNumber (str): card number
            debitAccount (str): your account number to transfer from

        Returns:
            success (ATMAccountNameResponseModal): ATM Account Name response

        Raises:
            MBBankAPIError: if api response not ok
        """
        card_id = self.getATMCardID(cardNumber=cardNumber)
        if card_id.errorInfo.code != "000":
            raise MBBankAPIError(
                {
                    "responseCode": card_id.errorInfo.code,
                    "message": card_id.errorInfo.message,
                }
            )
        bank_list = self.getBankList()
        bank_info: typing.Optional[Bank] = None
        for bank in bank_list.listBank:
            if cardNumber.startswith(bank.smlCode):
                bank_info = bank
                break
        if bank_info is None:
            raise BankNotFoundError("ATM Card Bank not found in bank list")
        json_data = {
            "creditAccount": card_id.cardID,
            "bankCode": bank_info.smlCode,
            "type": bank_info.typeTransfer,
            "creditAccountType": "CARD",
            "creditCardNo": cardNumber,
            "debitAccount": debitAccount,
            "remark": "",
        }
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/transfer/inquiryAccountName",
            json=json_data,
        )
        return ATMAccountNameResponseModal.model_validate(data_out, strict=True)

    def makeTransferAccountToAccount(
        self,
        *,
        src_account: str,
        dest_account: str,
        bank_code: str,
        amount: int,
        message: str,
    ) -> "TransferContext":
        """
        Make a transfer from src_account to dest_account

        Args:
            src_account (str): Source account number
            dest_account (str): Destination account number
            bank_code (str): Bank code of the destination account get from getBankList eg "MB".
            amount (int): Amount to transfer
            message (str): Transfer message
        """
        context = TransferContext(
            self,
            src_account=src_account,
            dest_account=dest_account,
            bank_code=bank_code,
            amount=amount,
            message=message,
        )
        return context.start()

    def userinfo(self) -> UserInfoResponseModal:
        """
        Get current user info

        Returns:
            success (UserInfoResponseModal): user info

        Raises:
            MBBankAPIError: if api response not ok
        """
        if self._userinfo is None:
            self._authenticate()
        return UserInfoResponseModal.model_validate(self._userinfo, strict=True)


class TransferContext:
    """
    Transfer context manager for account to account transfer

    Attributes:
        to_account_name (AccountNameResponseModal or None): destination account name info, this available when call makeTransferAccountToAccount
        refNo (str or None): reference number
        timestamp (str or None): timestamp
        transaction_authen (TransactionAuthenResponseModal or None): transaction authentication info
        mbbank (MBBank): MBBank instance
        src_account (str): source account number
        dest_account (str): destination account number
        bank_code (str): bank code of the destination account
        amount (int): amount to transfer
        message (str): transfer message
    """

    def __init__(
        self,
        mbbank_instance: MBBank,
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
        self.to_account_name = None
        self.refNo = None
        self.timestamp = None
        self.transaction_authen = None
        self.mbbank = mbbank_instance
        self.src_account = src_account
        self.dest_account = dest_account
        self.bank_code = bank_code
        self.amount = amount
        self.message = message
        self.bank = None

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
            self.getBank()
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

    def _craft_otp(self, otp: str, auth_type: AuthListItem) -> str:
        return f"ibr|{auth_type.code}||{otp}||{self.timestamp}|{self.transaction_authen.id}|{self.refNo}"

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
