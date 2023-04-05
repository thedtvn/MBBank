# MBBank API for Python
A unofficially light weight Python Api for the "Military Commercial Joint Stock Bank" account
## Requires
   [tesseract (windows)](https://github.com/UB-Mannheim/tesseract/wiki)
    
   [tesseract (Linux & Mac)](https://github.com/tesseract-ocr/tessdoc/blob/main/Installation.md)
 

   and python3
 
## Install
    pip install mbbank-lib
   or Dev Ver
   
    pip install git+https://github.com/thedtvn/MBBank

## How to Use
```py
import asyncio
import mbbank
import datetime

async def main():
    mb = mbbank.MbBank(username="<account number>", password="<account password>" [, tesseract_path="path/to/tesseract"])
    daynow = datetime.datetime.now()
    lasttime = daynow - datetime.timedelta(weeks=4*3) # maximum time 3 Month
    await mb.getTransactionAccountHistory(from_date=lasttime, to_date=daynow)
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
 

