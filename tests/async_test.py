import asyncio
import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mbbank import MBBankAsync


async def main():
    username = os.getenv("MBBANK_USERNAME")
    password = os.getenv("MBBANK_PASSWORD")

    if not username or not password:
        print("Please set MBBANK_USERNAME and MBBANK_PASSWORD environment variables.")
        sys.exit(1)

    mb = MBBankAsync(username=username, password=password)
    end_query_day = datetime.datetime.now()
    start_query_day = end_query_day - datetime.timedelta(days=30)
    await mb.getBalance()
    await mb.userinfo()
    await mb.getInterestRate()
    await mb.getAccountByPhone(username)
    await mb.getBankList()
    await mb.getBalanceLoyalty()
    await mb.getLoanList()
    for i in ["TRANSFER", "PAYMENT"]:
        for a in ["MOST", "LATEST"]:
            await mb.getFavorBeneficiaryList(transactionType=i, searchType=a)  # type: ignore this use typing.Literal
    card_list = await mb.getCardList()
    for i in card_list.cardList:
        await mb.getCardTransactionHistory(i.cardNo, start_query_day, end_query_day)
    saving_list = await mb.getSavingList()
    for i in saving_list.data.onlineFixedSaving.data:
        await mb.getSavingDetail(i.savingAccountNumber, "OSA")
    for i in saving_list.data.branchSaving.data:
        await mb.getSavingDetail(i.savingAccountNumber, "SBA")
    await mb.getTransactionAccountHistory(
        from_date=start_query_day, to_date=end_query_day
    )
    print("All async tests completed.")


asyncio.run(main())
