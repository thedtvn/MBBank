from typing import Optional, Any
from pydantic import BaseModel


class ErrorInfo(BaseModel):
    """
    Error Info Modal
    """

    code: str
    message: str
    target: Optional[Any] = None
    details: Optional[Any] = None


class ATMCardIDResponseModal(BaseModel):
    """
    ATM Card External Service Response Modal
    """

    responseID: str
    errorInfo: ErrorInfo
    cardID: Optional[str]
    cardNumber: Optional[str]
