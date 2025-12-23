"""
MBBank Python SDK
===================

A lightweight Python client for the MBBank API.

Features
--------
- **Async API** – [mbbank.asyncio](./mbbank/asyncio.html)
- **Sync API** – [mbbank.main](./mbbank/main.html)
- **Image Processing** – [mbbank.capcha_ocr](./mbbank/capcha_ocr.html)
- **Response Models** – [mbbank.modals](./mbbank/modals.html)
- **Errors** – [mbbank.errors](./mbbank/errors.html)

The package exposes the most commonly used classes at the top level for convenience.

Examples
--------

Note: All examples are using Sync API, but Async API is also available by using `MBBankAsync`.

Get transaction history of last 30 days

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
start_query_day = datetime.datetime.now()
# get transaction history of last 30 days
end_query_day = start_query_day - datetime.timedelta(days=30)
print(mb.getTransactionAccountHistory(from_date=start_query_day, to_date=end_query_day))
```

Get balance

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
print("Balance: ", mb.getBalance())
```

Get user info

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
print("User info: ", mb.userinfo())
```

Get interest rate

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
print("Interest rate: ", mb.getInterestRate())
```

Get account by phone

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
print("Account by phone: ", mb.getAccountByPhone("your_phone"))
```

Get bank list

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
print("Bank list: ", mb.getBankList())
```

Get balance loyalty

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
print("Balance loyalty: ", mb.getBalanceLoyalty())
```

Get loan list

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
print("Loan list: ", mb.getLoanList())
```

Get favor beneficiary list

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
print("Favor beneficiary list: ", mb.getFavorBeneficiaryList())
```

Get card list

```python
from mbbank import MBBank

mb = MBBank(
    username="your_username",
    password="your_password"
)
print("Card list: ", mb.getCardList())
```

More examples can be found on the [GitHub repository](https://github.com/thedtvn/MBBank/tree/main/examples).
"""

from .asyncio import MBBankAsync, TransferContextAsync
from .capcha_ocr import CapchaOCR, CapchaProcessing
from .main import MBBank, TransferContext

__all__ = [
    "MBBank",
    "TransferContext",
    "MBBankAsync",
    "TransferContextAsync",
    "CapchaProcessing",
    "CapchaOCR",
]

__version__ = "0.3.0"
