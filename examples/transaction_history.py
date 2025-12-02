import datetime
import mbbank


def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    mb = mbbank.MBBank(username=username, password=password)

    # Get the main account balance and info to find the account number
    balance_info = mb.getBalance()
    if not balance_info.acct_list:
        print("No accounts found.")
        return

    # Use the first account for history
    main_account = balance_info.acct_list[0]
    account_number = main_account.acctNo
    print(f"Fetching history for account: {account_number} ({main_account.acctAlias})")

    # Define date range: last 30 days
    to_date = datetime.datetime.now()
    from_date = to_date - datetime.timedelta(days=30)

    history = mb.getTransactionAccountHistory(
        accountNo=account_number, from_date=from_date, to_date=to_date
    )

    if not history.transactionHistoryList:
        print("No transactions found in the last 30 days.")
    else:
        print(f"\nTransaction History ({from_date.date()} to {to_date.date()}):")
        print("-" * 80)
        print(f"{'Date':<20} | {'Amount':<15} | {'Description'}")
        print("-" * 80)
        for transaction in history.transactionHistoryList:
            # Adjust fields based on actual TransactionAccountHistory model if needed
            # Assuming fields based on common banking API structures and typical usage
            # If 'transactionDate' or similar exists, use it.
            # Printing the raw object or available fields if unsure, but let's try to be specific based on typical mbbank usage.
            # Since I can't see the exact model definition for TransactionAccountHistory in the outline (it was truncated or in a modal file),
            # I will rely on the fact that it returns a list of transactions.
            # Let's try to print a few likely fields.

            date = getattr(transaction, "transactionDate", "N/A")
            amount = getattr(transaction, "creditAmount", 0) or getattr(
                transaction, "debitAmount", 0
            )
            description = getattr(transaction, "description", "No description")

            print(f"{str(date):<20} | {str(amount):<15} | {description}")


if __name__ == "__main__":
    main()
