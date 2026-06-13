"""
MBBank Python SDK
===================

A lightweight Python client for the MBBank API.

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

# Define version first to avoid circular imports
__version__ = "0.3.2"

import mbbank.aio as aio
import mbbank.base as base
import mbbank.capcha_ocr as capcha_ocr
import mbbank.encryption_backend as encryption_backend
import mbbank.errors as errors
import mbbank.modals as modals
import mbbank.sync as sync

from .aio import BulkTransferContextAsync, MBBankAsync, TransferContextAsync
from .capcha_ocr import CapchaOCR, CapchaProcessing
from .sync import BulkTransferContext, MBBank, TransferContext

__all__ = [
    "BulkTransferContext",
    "BulkTransferContextAsync",
    "CapchaOCR",
    "CapchaProcessing",
    "MBBank",
    "MBBankAsync",
    "TransferContext",
    "TransferContextAsync",
    "__version__",
    # Export submodules for documentation purposes
    "aio",
    "base",
    "capcha_ocr",
    "encryption_backend",
    "errors",
    "modals",
    "sync",
]
