import datetime
import base64
import hashlib
import typing
import requests
from .capcha_ocr import CapchaOCR, CapchaProcessing
from .wasm_helper import wasm_encrypt
from .modals import BalanceResponseModal, BalanceLoyaltyResponseModal, BankListResponseModal, \
    BeneficiaryListResponseModal, CardListResponseModal, AccountByPhoneResponseModal, UserInfoResponseModal, \
    LoanListResponseModal, SavingListResponseModal, InterestRateResponseModal, TransactionHistoryResponseModal \
    , CardTransactionsResponseModal, SavingDetailResponseModal

headers_default = {
    'Cache-Control': 'max-age=0',
    'Accept': 'application/json, text/plain, */*',
    'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
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


class MBBankError(Exception):
    def __init__(self, err_out):
        self.code = err_out['responseCode']
        self.message = err_out['message']
        super().__init__(f"{err_out['responseCode']} | {err_out['message']}")


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
    """

    FPR = "c7a1beebb9400375bb187daa33de9659"

    def __init__(self, *, username: str, password: str, proxy: dict = None, ocr_class=None):
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
        self.deviceIdCommon = f'i1vzyjp5-mbib-0000-0000-{self._get_now_time()}'

    def _get_now_time(self):
        now = datetime.datetime.now()
        microsecond = int(now.strftime("%f")[:2])
        return now.strftime(f"%Y%m%d%H%M{microsecond}")

    def _req(self, url, *, json=None, headers=None):
        if headers is None:
            headers = {}
        if json is None:
            json = {}
        while True:
            if self.sessionId is None:
                self._authenticate()
            rid = f"{self._userid}-{self._get_now_time()}"
            json_data = {
                'sessionId': self.sessionId if self.sessionId is not None else "",
                'refNo': rid,
                'deviceIdCommon': self.deviceIdCommon,
            }
            json_data.update(json)
            headers.update(headers_default)
            headers["X-Request-Id"] = rid
            headers["RefNo"] = rid
            headers["DeviceId"] = self.deviceIdCommon
            with requests.Session() as s:
                with s.post(url, headers=headers, json=json_data,
                            proxies=self.proxy) as r:
                    data_out = r.json()
            if data_out["result"] is None:
                self.getBalance()
            elif data_out["result"]["ok"]:
                data_out.pop("result", None)
                break
            elif data_out["result"]["responseCode"] == "GW200":
                self._authenticate()
            else:
                raise MBBankError(data_out["result"])
        return data_out

    def _get_wasm_file(self):
        if self._wasm_cache is not None:
            return self._wasm_cache
        file_data = requests.get("https://online.mbbank.com.vn/assets/wasm/main.wasm",
                                 proxies=self.proxy).content
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
            'sessionId': "",
            'refNo': rid,
            'deviceIdCommon': self.deviceIdCommon,
        }
        headers = headers_default.copy()
        headers["X-Request-Id"] = rid
        headers["Deviceid"] = self.deviceIdCommon
        headers["Refno"] = rid
        with requests.Session() as s:
            with s.post("https://online.mbbank.com.vn/retail-web-internetbankingms/getCaptchaImage",
                        headers=headers, json=json_data,
                        proxies=self.proxy) as r:
                data_out = r.json()
                return base64.b64decode(data_out["imageString"])

    def login(self, captcha_text: str):
        """
        Login to MBBank account

        Args:
            captcha_text (str): capcha text from capcha image

        Raises:
            MBBankError: if login failed
        """
        payload = {
            "userId": self._userid,
            "password": hashlib.md5(self._password.encode()).hexdigest(),
            "captcha": captcha_text,
            'sessionId': "",
            'refNo': f'{self._userid}-{self._get_now_time()}',
            'deviceIdCommon': self.deviceIdCommon,
            "ibAuthen2faString": self.FPR,
        }
        wasm_bytes = self._get_wasm_file()
        data_encrypt = wasm_encrypt(wasm_bytes, payload)
        with requests.Session() as s:
            with s.post("https://online.mbbank.com.vn/retail_web/internetbanking/doLogin",
                        headers=headers_default, json={"dataEnc": data_encrypt},
                        proxies=self.proxy) as r:
                data_out = r.json()
        if data_out["result"]["ok"]:
            self.sessionId = data_out["sessionId"]
            data_out.pop("result", None)
            self._userinfo = data_out
            return
        else:
            raise MBBankError(data_out["result"])

    def _authenticate(self):
        while True:
            self._userinfo = None
            self.sessionId = None
            self._temp = {}
            img_bytes = self.get_capcha_image()
            captcha_text = self.ocr_class.process_image(img_bytes)
            try:
                return self.login(captcha_text)
            except MBBankError as e:
                if e.code == "GW283":
                    continue  # capcha error, try again
                raise e

    def getTransactionAccountHistory(self, *, accountNo: str = None, from_date: datetime.datetime,
                                     to_date: datetime.datetime) -> TransactionHistoryResponseModal:
        """
        Get account transaction history

        Args:
            accountNo (str, optional): Sub account number Defaults to Main Account number.
            from_date (datetime.datetime): transaction from date
            to_date (datetime.datetime): transaction to date

        Returns:
            success (TransactionHistoryResponseModal): account transaction history

        Raises:
            MBBankError: if api response not ok
        """
        if self._userinfo is None:
            self._authenticate()
        json_data = {
            'accountNo': self._userid if accountNo is None else accountNo,
            'fromDate': from_date.strftime("%d/%m/%Y"),
            'toDate': to_date.strftime("%d/%m/%Y"),  # max 3 months
        }
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail-transactionms/transactionms/get-account-transaction-history",
            json=json_data)
        return TransactionHistoryResponseModal.model_validate(data_out, strict=True)

    def getBalance(self) -> BalanceResponseModal:
        """
        Get all main account and subaccount balance

        Returns:
            success (BalanceResponseModal): balance model

        Raises:
            MBBankError: if api response not ok
        """
        if self._userinfo is None:
            self._authenticate()
        data_out = self._req("https://online.mbbank.com.vn/api/retail-web-accountms/getBalance")
        return BalanceResponseModal.model_validate(data_out, strict=True)

    def getBalanceLoyalty(self) -> BalanceLoyaltyResponseModal:
        """
        Get Account loyalty rank and Member loyalty point

        Returns:
            success (BalanceLoyaltyResponseModal): loyalty balance model

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/loyalty/getBalanceLoyalty")
        return BalanceLoyaltyResponseModal.model_validate(data_out, strict=True)

    def getInterestRate(self, currency: str = "VND") -> InterestRateResponseModal:
        """
        Get saving interest rate

        Args:
            currency (str, optional): currency ISO 4217 format. Defaults to "VND" (Vietnam Dong).

        Returns:
            success (InterestRateResponseModal): interest rate

        Raises:
            MBBankError: if api response not ok
        """
        json_data = {
            "productCode": "TIENGUI.KHN.EMB",
            "currency": currency,
        }
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/saving/getInterestRate", json=json_data)
        return InterestRateResponseModal.model_validate(data_out, strict=True)

    def getFavorBeneficiaryList(self, *, transactionType: typing.Literal["TRANSFER", "PAYMENT"],
                                searchType: typing.Literal["MOST", "LATEST"]) -> UserInfoResponseModal:
        """
        Get all favor or most transfer beneficiary list from your account

        Args:
            transactionType (Literal["TRANSFER", "PAYMENT"]): transaction type
            searchType (Literal["MOST", "LATEST"]): search type

        Returns:
            success (UserInfoResponseModal): favor beneficiary list

        Raises:
            MBBankError: if api response not ok
        """
        json_data = {
            "transactionType": transactionType,
            "searchType": searchType
        }
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/internetbanking/getFavorBeneficiaryList", json=json_data)
        return BeneficiaryListResponseModal.model_validate(data_out, strict=True)

    def getCardList(self) -> CardListResponseModal:
        """
        Get all card list from your account

        Returns:
            success (CardListResponseModal): card list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/card/getList")
        return CardListResponseModal.model_validate(data_out, strict=True)

    def getSavingList(self) -> SavingListResponseModal:
        """
        Get all saving list from your account

        Returns:
            success (SavingListResponseModal): saving list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/saving/getList")
        return SavingListResponseModal.model_validate(data_out, strict=True)

    def getSavingDetail(self, accNo: str, accType: typing.Literal["OSA", "SBA"]) -> SavingDetailResponseModal:
        """
        Get saving detail by account number

        Args:
            accNo (str): saving account number
            accType (Literal["OSA", "SBA"]): saving account type | OSA: Online Saving Account, SBA: Saving Bank Account

        Returns:
            success (c): saving detail

        Raises:
            MBBankError: if api response not ok
        """
        json_data = {
            "accNo": accNo,
            "accType": accType
        }
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/saving/getDetail", json=json_data)
        return SavingDetailResponseModal.model_validate(data_out, strict=True)

    def getLoanList(self) -> LoanListResponseModal:
        """
        Get all loan list from your account

        Returns:
            success (LoanListResponseModal): loan list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail-web-onlineloanms/loan/getList")
        return LoanListResponseModal.model_validate(data_out, strict=True)

    def getCardTransactionHistory(self, cardNo: str, from_date: datetime.datetime,
                                  to_date: datetime.datetime) -> CardTransactionsResponseModal:
        """
        Get card transaction history

        Args:
            cardNo (str): card number get from getCardList
            from_date (datetime.datetime): from date
            to_date (datetime.datetime): to date

        Returns:
            success (CardListResponseModal): card transaction history

        Raises:
            MBBankError: if api response not ok
        """
        json_data = {
            "accountNo": cardNo,
            "fromDate": from_date.strftime("%d/%m/%Y"),
            "toDate": to_date.strftime("%d/%m/%Y"),  # max 3 months
            "historyNumber": "",
            "historyType": "DATE_RANGE",
            "type": "CARD",
        }
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/common/getTransactionHistory", json=json_data)
        return CardTransactionsResponseModal.model_validate(data_out, strict=True)

    def getBankList(self) -> BankListResponseModal:
        """
        Get transfer all bank list

        Returns:
            success (BankListResponseModal): bank list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/common/getBankList")
        return BankListResponseModal.model_validate(data_out, strict=True)

    def getAccountByPhone(self, phone: str) -> AccountByPhoneResponseModal:
        """
        Get transfer account info by phone (MBank internal account only)

        Args:
            phone (str): MBBank account phone number

        Returns:
            success (AccountByPhoneResponseModal): account info

        Raises:
            MBBankError: if api response not ok
        """
        json_data = {
            "phone": phone
        }
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/common/getAccountByPhone", json=json_data)
        return AccountByPhoneResponseModal.model_validate(data_out, strict=True)

    def userinfo(self) -> UserInfoResponseModal:
        """
        Get current user info

        Returns:
            success (UserInfoResponseModal): user info

        Raises:
            MBBankError: if api response not ok
        """
        if self._userinfo is None:
            self._authenticate()
        return UserInfoResponseModal.model_validate(self._userinfo, strict=True)
