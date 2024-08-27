import asyncio
import datetime
import os

from mbbank import MBBankAsync


async def main():
    mb = MBBankAsync(username=os.getenv("MBBANK_USERNAME"), password=os.getenv("MBBANK_PASSWORD"))
    end_query_day = datetime.datetime.now()
    start_query_day = end_query_day - datetime.timedelta(days=30)
    await mb.getBalance()
    await mb.userinfo()
    await mb.getInterestRate()
    await mb.getAccountByPhone(os.getenv("MBBANK_USERNAME"))
    await mb.getBankList()
    await mb.getBalanceLoyalty()
    await mb.getLoanList()
    await mb.getSavingList()
    for i in ["TRANSFER", "PAYMENT"]:
        for a in ["MOST", "LATEST"]:
            await mb.getFavorBeneficiaryList(transactionType=i, searchType=a)
    card_list = await mb.getCardList()
    for i in card_list["cardList"]:
        await mb.getCardTransactionHistory(i["cardNo"], start_query_day, end_query_day)
    await mb.getTransactionAccountHistory(from_date=start_query_day, to_date=end_query_day)


asyncio.run(main())
