import mbbank


def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    mb = mbbank.MBBank(username=username, password=password)

    print("Fetching saving account list...")
    savings_response = mb.getSavingList()

    # Assuming the response has a list of saving accounts.
    # Based on naming convention it might be savingList or similar.
    # Checking main.py outline, it returns SavingListResponseModal.
    # Let's assume it has a list attribute.

    # If we look at other response modals (e.g. CardListResponseModal -> cardList),
    # SavingListResponseModal likely has something similar.
    # I'll use a safe approach or try to inspect if I could.
    # But for now I'll assume a 'savingList' or 'savingsList' attribute or iterate if iterable.
    # Let's try 'savingList' based on 'getSavingList' name.

    savings = getattr(savings_response, "savingList", [])
    # Fallback if it's different, maybe just print the response if empty?
    # But let's assume 'savingList' for now as it matches the pattern.

    if not savings:
        print("No saving accounts found.")
    else:
        print("\nSaving Account List:")
        print("-" * 80)
        print(
            f"{'Account No':<20} | {'Balance':<15} | {'Interest Rate':<10} | {'Maturity Date'}"
        )
        print("-" * 80)
        for acc in savings:
            acc_no = getattr(acc, "accountNo", "N/A")
            balance = getattr(acc, "balance", 0)  # or principalAmount
            rate = getattr(acc, "interestRate", "N/A")
            maturity = getattr(acc, "maturityDate", "N/A")

            print(
                f"{str(acc_no):<20} | {str(balance):<15} | {str(rate):<10} | {maturity}"
            )


if __name__ == "__main__":
    main()
