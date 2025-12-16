# Use for error that does not have message and need custom message

custom_messages = {"MC3011": "Card not found."}


class MBBankAPIError(Exception):
    """
    MBBank Api Error Exception

    Attributes:
        code (str): The error code returned by the API.
        message (str): The error message associated with the error code.
    """

    def __init__(self, err_out):
        self.code = err_out["responseCode"]
        if self.code in custom_messages.keys():
            self.message = custom_messages[self.code]
        else:
            self.message = err_out["message"]
        super().__init__(f"{self.code} | {self.message}")


class MBBankError(Exception):
    """
    MBBank Lib Internal Error Exception
    """

    def __init__(self, err_out):
        super().__init__(err_out)


class CapchaError(Exception):
    """
    Capcha Error Exception
    """

    def __init__(self, err_out):
        super().__init__(err_out)


class BankNotFoundError(Exception):
    """
    Card Bank Not Found Error Exception
    """

    def __init__(self, err_out):
        super().__init__(err_out)


class CryptoVerifyError(Exception):
    """
    Crypto Verify Error Exception
    This error is raised when the crypto verification is required.
    ( temporary for who wants to try to reverse engineer )

    Attributes:
        resp_out (str): The response output that requires crypto verification.
        content_type (str): The content type of the response.
    """

    resp_out: str
    content_type: str

    def __init__(self, resp_out: str, content_type: str):
        self.content_type = content_type
        self.resp_out = resp_out
        super().__init__(
            "Crypto verification is required. This feature is not supported yet and is for advanced users who want to reverse engineer the webapp."
        )
