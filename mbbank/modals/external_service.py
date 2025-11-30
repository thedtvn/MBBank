from typing import Optional, Any
from pydantic import BaseModel


class ErrorInfo(BaseModel):
    code: str
    message: str
    target: Optional[Any] = None
    details: Optional[Any] = None


class ATMCardIDResponseModal(BaseModel):
    responseID: str
    errorInfo: ErrorInfo
    cardID: Optional[str]
    cardNumber: Optional[str]