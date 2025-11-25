class MBBankError(Exception):
    def __init__(self, err_out):
        self.code = err_out['responseCode']
        self.message = err_out['message']
        super().__init__(f"{err_out['responseCode']} | {err_out['message']}")


class CapchaError(MBBankError):
    def __init__(self, err_out):
        super().__init__(err_out)
