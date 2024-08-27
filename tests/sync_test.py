import datetime
import os
from mbbank import MBBank

mb = MBBank(username=os.getenv("MBBANK_USERNAME"), password=os.getenv("MBBANK_PASSWORD"))
end_query_day = datetime.datetime.now()
start_query_day = end_query_day - datetime.timedelta(days=30)
mb.getBalance()
mb.userinfo()
mb.getInterestRate()
mb.getAccountByPhone(os.getenv("MBBANK_USERNAME"))
mb.getBankList()
mb.getBalanceLoyalty()
mb.getLoanList()
mb.getSavingList()
for i in ["TRANSFER", "PAYMENT"]:
    for a in ["MOST", "LATEST"]:
        mb.getFavorBeneficiaryList(transactionType=i, searchType=a)
card_list = mb.getCardList()
for i in card_list["cardList"]:
    mb.getCardTransactionHistory(i["cardNo"], start_query_day, end_query_day)
mb.getTransactionAccountHistory(from_date=start_query_day, to_date=end_query_day)
