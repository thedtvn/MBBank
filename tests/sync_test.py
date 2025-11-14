import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mbbank import MBBank

username = os.getenv("MBBANK_USERNAME")
password = os.getenv("MBBANK_PASSWORD")

if not username or not password:
    print("Please set MBBANK_USERNAME and MBBANK_PASSWORD environment variables.")
    sys.exit(1)

mb = MBBank(username=username, password=password)
end_query_day = datetime.datetime.now()
start_query_day = end_query_day - datetime.timedelta(days=30)
mb.getBalance()
mb.userinfo()
mb.getInterestRate()
mb.getAccountByPhone(username)
mb.getBankList()
mb.getBalanceLoyalty()
mb.getLoanList()
for i in ["TRANSFER", "PAYMENT"]:
    for a in ["MOST", "LATEST"]:
        mb.getFavorBeneficiaryList(transactionType=i, searchType=a) # type: ignore this use typing.Literal
card_list = mb.getCardList()
for i in card_list.cardList:
    mb.getCardTransactionHistory(i.cardNo, start_query_day, end_query_day)
saving_list = mb.getSavingList()
for i in saving_list.data.onlineFixedSaving.data:
    mb.getSavingDetail(i.savingAccountNumber, "OSA")
for i in saving_list.data.branchSaving.data:
    mb.getSavingDetail(i.savingAccountNumber, "SBA")
mb.getTransactionAccountHistory(from_date=start_query_day, to_date=end_query_day)
print("All sync tests completed.")
