# MBBank API for Python
A unofficially light weight Python Api for the "Military Commercial Joint Stock Bank" account

## why we  have this lib ?

Because I don't want to lose money on some api services like [casso.vn](https://casso.vn/)

## Requires
   [tesseract (windows)](https://github.com/UB-Mannheim/tesseract/wiki)
    
   [tesseract (Linux & Mac)](https://github.com/tesseract-ocr/tessdoc/blob/main/Installation.md)
 

   and python3
 
## Install
    pip install mbbank-lib
   or Dev Ver
   
    pip install git+https://github.com/thedtvn/MBBank

## How to Use

### sync
```py
import datetime
import mbbank

mb = mbbank.MBBank(username="<account number>", password="<account password>" [, tesseract_path="path/to/tesseract"])
daynow = datetime.datetime.now()
lasttime = daynow - datetime.timedelta(weeks=4*3) # maximum time 3 Month
mb.getTransactionAccountHistory(from_date=lasttime, to_date=daynow [, accountNo="<sub account number default is main account number>"])
mb.getBalance()
mb.getBalanceLoyalty()
mb.getInterestRate()
mb.getFavorBeneficiaryList(transactionType= "TRANSFER" or "PAYMENT", searchType="MOST" or "LATEST")
mb.getCardList()
mb.getSavingList()
mb.getLoanList()
mb.userinfo()
```

### async
```py
import asyncio
from mbbank import mb_async as mbbank
import datetime

async def main():
    mb = mbbank.MBBank(username="<account number>", password="<account password>" [, tesseract_path="path/to/tesseract"])
    daynow = datetime.datetime.now()
    lasttime = daynow - datetime.timedelta(weeks=4*3) # maximum time 3 Month
    await mb.getTransactionAccountHistory(from_date=lasttime, to_date=daynow [, accountNo="<sub account number default is main account number>"])
    await mb.getBalance()
    await mb.getBalanceLoyalty()
    await mb.getInterestRate()
    await mb.getFavorBeneficiaryList(transactionType= "TRANSFER" or "PAYMENT", searchType="MOST" or "LATEST")
    await mb.getCardList()
    await mb.getSavingList()
    await mb.getLoanList()
    await mb.userinfo()

asyncio.run(main())
```
and all this is return json for you have full control your data

![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fthedtvn%2FMBBank&count_bg=%2379C83D&title_bg=%23555555&icon=python.svg&icon_color=%23E7E7E7&title=Views+Counter&edge_flat=false)