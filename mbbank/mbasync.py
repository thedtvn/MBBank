from PIL import Image
import pytesseract
import re
import datetime
import base64
import hashlib
import typing
import io
import platform
import aiohttp
from .main import MBBankError

headers_default = {
    'Cache-Control': 'no-cache',
    'Accept': 'application/json, text/plain, */*',
    'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
    'User-Agent': f'Mozilla/5.0 (X11; {platform.system()} {platform.processor()})',
    "Origin": "https://online.mbbank.com.vn",
    "Referer": "https://online.mbbank.com.vn/"
}


def get_now_time():
    now = datetime.datetime.now()
    microsecond = int(now.strftime("%f")[:2])
    return now.strftime(f"%Y%m%d%H%M{microsecond}")


class MBBankAsync:
    """Core Async class

    Attributes:
        deviceIdCommon (str): Device id common
        sessionId (str or None): Current Session id

    Args:
        username (str): MBBank Account Username
        password (str): MBBank Account Password
        tesseract_path (str, optional): Tesseract path. Defaults to None.
    """
    deviceIdCommon = f'i1vzyjp5-mbib-0000-0000-{get_now_time()}'

    def __init__(self, *, username, password, tesseract_path=None):
        self.__userid = username
        self.__password = password
        if tesseract_path is not None:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.sessionId = None
        self._userinfo = None
        self._temp = {}

    async def _req(self, url, *, json={}, headers={}):
        while True:
            if self.sessionId is None:
                await self._authenticate()
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
            async with aiohttp.ClientSession() as s:
                async with s.post(url, headers=headers, json=json_data) as r:
                    data_out = await r.json()
            if data_out["result"] is None:
                await self.getBalance()
            elif data_out["result"]["ok"]:
                data_out.pop("result", None)
                break
            elif data_out["result"]["responseCode"] == "GW200":
                await self._authenticate()
            else:
                err_out = data_out["result"]
                raise MBBankError(err_out)
        return data_out

    async def _authenticate(self):
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
            async with aiohttp.ClientSession() as s:
                async with s.post("https://online.mbbank.com.vn/retail-web-internetbankingms/getCaptchaImage",
                                  headers=headers, json=json_data) as r:
                    data_out = await r.json()
            img_byte = io.BytesIO(base64.b64decode(data_out["imageString"]))
            img = Image.open(img_byte)
            img = img.convert('RGBA')
            pix = img.load()
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    if pix[x, y][0] < 102 or pix[x, y][1] < 102 or pix[x, y][2] < 102:
                        pix[x, y] = (0, 0, 0, 255)
                    else:
                        pix[x, y] = (255, 255, 255, 255)
            text = pytesseract.image_to_string(img)
            text = re.sub(r"\s+", "", text, flags=re.MULTILINE)
            payload = {
                "userId": self.__userid,
                "password": hashlib.md5(self.__password.encode()).hexdigest(),
                "captcha": text,
                'sessionId': "",
                'refNo': f'{self.__userid}-{get_now_time()}',
                'deviceIdCommon': self.deviceIdCommon,
            }
            async with aiohttp.ClientSession() as s:
                async with s.post("https://online.mbbank.com.vn/retail_web/internetbanking/doLogin",
                                  headers=headers_default, json=payload) as r:
                    data_out = await r.json()
            if data_out["result"]["ok"]:
                self.sessionId = data_out["sessionId"]
                self._userinfo = data_out
                return
            elif data_out["result"]["responseCode"] == "GW283":
                pass
            else:
                err_out = data_out["result"]
                raise Exception(f"{err_out['responseCode']} | {err_out['message']}")

    async def getTransactionAccountHistory(self, *, accountNo: str = None, from_date: datetime.datetime,
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
        json_data = {
            'accountNo': self.__userid if accountNo is None else accountNo,
            'fromDate': from_date.strftime("%d/%m/%Y"),
            'toDate': to_date.strftime("%d/%m/%Y"),  # max 3 months
        }
        data_out = await self._req(
            "https://online.mbbank.com.vn/api/retail-transactionms/transactionms/get-account-transaction-history",
            json=json_data)
        return data_out

    async def getBalance(self):
        """
        Get all main account and sub account balance

        Returns:
            success (dict): list account balance

        Raises:
            MBBankError: if api response not ok
        """
        data_out = await self._req("https://online.mbbank.com.vn/api/retail-web-accountms/getBalance")
        return data_out

    async def getBalanceLoyalty(self):
        """
        Get Account loyalty rank and Member loyalty point

        Returns:
            success (dict): loyalty point

        Raises:
            MBBankError: if api response not ok
        """
        data_out = await self._req("https://online.mbbank.com.vn/api/retail_web/loyalty/getBalanceLoyalty")
        return data_out

    async def getInterestRate(self, currency: str = "VND"):
        """
        Get saving interest rate

        Args:
            currency (str, optional): currency ISO 4217 format. Defaults to "VND" (Viet Nam Dong).

        Returns:
            success (dict): interest rate

        Raises:
            MBBankError: if api response not ok
        """
        json_data = {
            "productCode": "TIENGUI.KHN.EMB",
            "currency": currency
        }
        data_out = await self._req("https://online.mbbank.com.vn/api/retail_web/saving/getInterestRate", json=json_data)
        return data_out

    async def getFavorBeneficiaryList(self, *, transactionType: typing.Literal["TRANSFER", "PAYMENT"],
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
        data_out = await self._req(
            "https://online.mbbank.com.vn/api/retail_web/internetbanking/getFavorBeneficiaryList", json=json_data)
        return data_out

    async def getCardList(self):
        """
        Get all card list from your account

        Returns:
            success (dict): card list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = await self._req("https://online.mbbank.com.vn/api/retail_web/card/getList")
        return data_out

    async def getSavingList(self):
        """
        Get all saving list from your account

        Returns:
            success (dict): saving list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = await self._req("https://online.mbbank.com.vn/api/retail_web/saving/getList")
        return data_out

    async def getLoanList(self):
        """
        Get all loan list from your account

        Returns:
            success (dict): loan list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = await self._req("https://online.mbbank.com.vn/api/retail_web/loan/getList")
        return data_out

    async def getCardTransactionHistory(self, cardNo: str, from_date: datetime.datetime, to_date: datetime.datetime):
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
        data_out = await self._req("https://online.mbbank.com.vn/api/retail_web/common/getTransactionHistory",
                                   json=json_data)
        return data_out

    async def getBankList(self):
        """
        Get transfer all bank list

        Returns:
            success (dict): bank list

        Raises:
            MBBankError: if api response not ok
        """
        data_out = await self._req("https://online.mbbank.com.vn/api/retail_web/common/getBankList")
        return data_out

    async def getAccountByPhone(self, phone: str):
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
        data_out = await self._req("https://online.mbbank.com.vn/api/retail_web/common/getAccountByPhone",
                                   json=json_data)
        return data_out

    async def userinfo(self):
        """
        Get current user info

        Returns:
            success (dict): user info

        Raises:
            MBBankError: if api response not ok
        """
        if self._userinfo is None:
            await self._authenticate()
        else:
            await self.getBalance()
        return self._userinfo
