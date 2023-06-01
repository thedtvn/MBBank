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
    
    # get user name for tranfer money
    
    bankList = await mb.getBankList()
    for i in bankList["listBank"]:
        if i["bankId"] == "MB":
            mbbankid = i
            break
    # get name by Account nuber
    await mb.inquiryAccountName(typeTransfer=mbbankid["typeTransfer"], bankCode=mbbankid["smlCode"], creditAccountType="ACCOUNT", debitAccount="your Account nuber", creditAccount="Account you what to get name")
    # get name by Card nuber (napas)
    await mb.inquiryAccountName(creditAccountType="CARD", debitAccount="your Account nuber", creditAccount="Account you what to get name")



asyncio.run(main())
```
and all this is return json for you have full control your data


## TODO

- [ ] add tranfer money

![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fthedtvn%2FMBBank&count_bg=%2379C83D&title_bg=%23555555&icon=python.svg&icon_color=%23E7E7E7&title=Views+Counter&edge_flat=false)