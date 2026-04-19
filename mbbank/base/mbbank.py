import datetime
import typing

from mbbank.capcha_ocr import CapchaOCR, CapchaProcessing


class MBBankBase:
    """Base class with shared attributes and utility methods for MBBank sync/async implementations.

    Attributes:
        deviceIdCommon (str): Device id common
        sessionId (str or None): Current Session id

    Args:
        username (str): MBBank Account Username
        password (str): MBBank Account Password
        ocr_class (CapchaProcessing, optional): instance of CapchaProcessing class. Defaults to CapchaOCR().
        retry_times (int, optional): number of retry times for capcha processing. Defaults to 30 ( worst case ).
    """

    FPR = "c7a1beebb9400375bb187daa33de9659"

    HEADERS_DEFAULT = {
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

    def __init__(
        self,
        *,
        username: str,
        password: str,
        ocr_class: typing.Optional[CapchaProcessing] = None,
        retry_times: int = 30,
    ):
        self._userid = username
        self._password = password
        self._wasm_cache: typing.Optional[bytes] = None
        self.ocr_class: CapchaProcessing = CapchaOCR()
        if ocr_class is not None:
            if not isinstance(ocr_class, CapchaProcessing):
                raise ValueError("ocr_class must be instance of CapchaProcessing")
            self.ocr_class = ocr_class
        self.sessionId: typing.Optional[str] = None
        self._userinfo: typing.Optional[dict] = None
        self._temp: dict = {}
        self.deviceIdCommon = f"abi2jojr-mbib-0000-0000-{self._get_now_time()}"
        self.retry_times = retry_times

    def _get_now_time(self) -> str:
        now = datetime.datetime.now()
        microsecond = int(now.strftime("%f")[:2])
        return now.strftime(f"%Y%m%d%H%M{microsecond}")
