# Use for error that dose not have message and need custom message
custom_messages = {"MC3011": "Card not found."}


class MBBankAPIError(Exception):
    """
    MBBank Api Error Exception
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
