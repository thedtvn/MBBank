# mbbank.MBBankAsync(username, password, tesseract_path)
:   Core Async class

 **Attributes**

deviceIdCommon (str): Device id common

sessionId (str or None): Current Session id

 **Parameters**

`username` (str): MBBank Account Username

`password` (str): MBBank Account Password

`tesseract_path` (str): Tesseract path. Defaults to None.


### async getBalance()
:   Get all main account and sub account balance

 **Returns**

    success (dict): list account balance

 **Raises**

    MBBankError: if api response not ok


### async getBalanceLoyalty()
:   Get Account loyalty rank and Member loyalty point

 **Returns**

    success (dict): loyalty point

 **Raises**

    MBBankError: if api response not ok


### async getCardList()
:   Get all card list from your account

 **Returns**

    success (dict): card list

 **Raises**

    MBBankError: if api response not ok


### async getCardTransactionHistory(cardNo, from_date, to_date)
:   Get card transaction history

 **Parameters**

`cardNo` (str): card number get from getCardList

`from_date` (datetime.datetime): from date

`to_date` (datetime.datetime): to date

 **Returns**

    success (dict): card transaction history

 **Raises**

    MBBankError: if api response not ok


### async getFavorBeneficiaryList(transactionType, searchType)
:   Get all favor or most transfer beneficiary list from your account

 **Parameters**

`transactionType` (Literal["TRANSFER", "PAYMENT"]): transaction type

`searchType` (Literal["MOST", "LATEST"]): search type

 **Returns**

    success (dict): favor beneficiary list

 **Raises**

    MBBankError: if api response not ok


### async getInterestRate(currency)
:   Get saving interest rate

 **Parameters**

`currency` (str): currency ISO 4217 format. Defaults to "VND" (Viet Nam Dong).

 **Returns**

    success (dict): interest rate

 **Raises**

    MBBankError: if api response not ok


### async getLoanList()
:   Get all loan list from your account

 **Returns**

    success (dict): loan list

 **Raises**

    MBBankError: if api response not ok


### async getSavingList()
:   Get all saving list from your account

 **Returns**

    success (dict): saving list

 **Raises**

    MBBankError: if api response not ok


### async getTransactionAccountHistory(accountNo, from_date, to_date)
:   Get account transaction history

 **Parameters**

`accountNo` (str): Sub account number Defaults to Main Account number.

`from_date` (datetime.datetime): transaction from date

`to_date` (datetime.datetime): transaction to date

 **Returns**

    success (dict): account transaction history

 **Raises**

    MBBankError: if api response not ok


### async userinfo()
:   Get current user info

 **Returns**

    success (dict): user info

 **Raises**

    MBBankError: if api response not ok
