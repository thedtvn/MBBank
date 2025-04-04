import datetime
import base64
import hashlib
import typing
import requests
from .capcha_ocr import CapchaOCR, CapchaProcessing
from .wasm_helper import wasm_encrypt

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


def get_now_time():
    now = datetime.datetime.now()
    microsecond = int(now.strftime("%f")[:2])
    return now.strftime(f"%Y%m%d%H%M{microsecond}")


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
        ocr_class (CapchaProcessing, optional): CapchaProcessing class. Defaults to TesseractOCR().
    """
    deviceIdCommon = f'i1vzyjp5-mbib-0000-0000-{get_now_time()}'
    FPR = "c7a1beebb9400375bb187daa33de9659"

    def __init__(self, *, username, password, proxy=None, ocr_class=None):
        self.__userid = username
        self.__password = password
        self.__wasm_cache = None
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

    def _req(self, url, *, json=None, headers=None):
        if headers is None:
            headers = {}
        if json is None:
            json = {}
        while True:
            if self.sessionId is None:
                self._authenticate()
            rid = f"{self.__userid}-{get_now_time()}"
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
                err_out = data_out["result"]
                raise MBBankError(err_out)
        return data_out

    def _get_wasm_file(self):
        if self.__wasm_cache is not None:
            return self.__wasm_cache
        file_data = requests.get("https://online.mbbank.com.vn/assets/wasm/main.wasm",
                                 proxies=self.proxy).content
        self.__wasm_cache = file_data
        return file_data

    def _authenticate(self):
        while True:
            self._userinfo = None
            self.sessionId = None
            self._temp = {}
            rid = f"{self.__userid}-{get_now_time()}"
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
            img_bytes = base64.b64decode(data_out["imageString"])
            text = self.ocr_class.process_image(img_bytes)
            payload = {
                "userId": self.__userid,
                "password": hashlib.md5(self.__password.encode()).hexdigest(),
                "captcha": text,
                'sessionId': "",
                'refNo': f'{self.__userid}-{get_now_time()}',
                'deviceIdCommon': self.deviceIdCommon,
                "ibAuthen2faString": self.FPR,
            }
            wasm_bytes = self._get_wasm_file()
            dataEnc = wasm_encrypt(wasm_bytes, payload)
            with requests.Session() as s:
                with s.post("https://online.mbbank.com.vn/retail_web/internetbanking/doLogin",
                            headers=headers_default, json={"dataEnc": dataEnc},
                            proxies=self.proxy) as r:
                    data_out = r.json()
            if data_out["result"]["ok"]:
                self.sessionId = data_out["sessionId"]
                self._userinfo = data_out
                return
            elif data_out["result"]["responseCode"] == "GW283":
                pass
            else:
                err_out = data_out["result"]
                raise Exception(f"{err_out['responseCode']} | {err_out['message']}")

    def getTransactionAccountHistory(self, *, accountNo: str = None, from_date: datetime.datetime,
                                     to_date: datetime.datetime):
        """
        Get account transaction history

        Args:
            accountNo (str, optional): Sub account number Defaults to Main Account number.
            from_date (datetime.datetime): transaction from date
            to_date (datetime.datetime): transaction to date

        Returns:
            success (dict): account transaction history

        Raises:
            MBBankError: if api response not ok
        """
        if self._userinfo is None:
            self._authenticate()
        json_data = {
            'accountNo': self.__userid if accountNo is None else accountNo,
            'fromDate': from_date.strftime("%d/%m/%Y"),
            'toDate': to_date.strftime("%d/%m/%Y"),  # max 3 months
        }
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail-transactionms/transactionms/get-account-transaction-history",
            json=json_data)
        return data_out

    def getBalance(self):
        """
        Get all main account and subaccount balance

        Returns:
            success (dict): list account balance

        Raises:
            MBBankError: if api response not ok
        """
        if self._userinfo is None:
            self._authenticate()
        data_out = self._req("https://online.mbbank.com.vn/api/retail-web-accountms/getBalance")
        return data_out

    def getBalanceLoyalty(self):
        """
        Get Account loyalty rank and Member loyalty point

        Returns:
            success (dict): loyalty point

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/loyalty/getBalanceLoyalty")
        return data_out

    def getInterestRate(self, currency: str = "VND"):
        """
        Get saving interest rate

        Args:
            currency (str, optional): currency ISO 4217 format. Defaults to "VND" (Vietnam Dong).

        Returns:
            success (dict): interest rate

        Raises:
            MBBankError: if api response not ok
        """
        json_data = {
            "productCode": "TIENGUI.KHN.EMB",
            "currency": currency,
        }
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/saving/getInterestRate", json=json_data)
        return data_out

    def getFavorBeneficiaryList(self, *, transactionType: typing.Literal["TRANSFER", "PAYMENT"],
                                searchType: typing.Literal["MOST", "LATEST"]):
        """
        Get all favor or most transfer beneficiary list from your account

        Args:
            transactionType (Literal["TRANSFER", "PAYMENT"]): transaction type
            searchType (Literal["MOST", "LATEST"]): search type

        Returns:
            success (dict): favor beneficiary list

        Raises:
            MBBankError: if api response not ok
        """
        json_data = {
            "transactionType": transactionType,
            "searchType": searchType
        }
        data_out = self._req(
            "https://online.mbbank.com.vn/api/retail_web/internetbanking/getFavorBeneficiaryList", json=json_data)
        return data_out

    def getCardList(self):
        """
        Get all card list from your account

        Returns:
            success (dict): card list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/card/getList")
        return data_out

    def getSavingList(self):
        """
        Get all saving list from your account

        Returns:
            success (dict): saving list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/saving/getList")
        return data_out

    def getLoanList(self):
        """
        Get all loan list from your account

        Returns:
            success (dict): loan list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail-web-onlineloanms/loan/getList")
        return data_out

    def getCardTransactionHistory(self, cardNo: str, from_date: datetime.datetime, to_date: datetime.datetime):
        """
        Get card transaction history

        Args:
            cardNo (str): card number get from getCardList
            from_date (datetime.datetime): from date
            to_date (datetime.datetime): to date

        Returns:
            success (dict): card transaction history

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
        return data_out

    def getBankList(self):
        """
        Get transfer all bank list

        Returns:
            success (dict): bank list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/common/getBankList")
        return data_out

    def getAccountByPhone(self, phone: str):
        """
        Get transfer account info by phone (MBank internal account only)

        Args:
            phone (str): MBBank account phone number

        Returns:
            success (dict): account info

        """
        json_data = {
            "phone": phone
        }
        data_out = self._req("https://online.mbbank.com.vn/api/retail_web/common/getAccountByPhone", json=json_data)
        return data_out

    def userinfo(self):
        """
        Get current user info

        Returns:
            success (dict): user info

        Raises:
            MBBankError: if api response not ok
        """
        if self._userinfo is None:
            self._authenticate()
        else:
            self.getBalance()
        return self._userinfo
