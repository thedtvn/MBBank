import mbbank

# requires 'qrcode[pil]' package for QR code generation
import qrcode

username = input("Enter your username: ")
password = input("Enter your password: ")

mb = mbbank.MBBank(username=username, password=password)


def get_auth_method(mb: mbbank.MBBank):
    """
    Prompt user to select authentication method for transfer.
    """
    auth_methods = transfer_ctx.get_auth_list()

    print("Available authentication methods:")

    for idx, method in enumerate(auth_methods.authList):
        print(f"{idx + 1}. {method.name}")

    auth_idx = int(input("Select the authentication method number: ")) - 1
    return auth_methods.authList[auth_idx]


def get_bank_to(mb: mbbank.MBBank):
    """
    Prompt user to select destination bank for transfer.
    """
    banks = mb.getBankList()
    print("Available Banks:")

    for idx, bank in enumerate(banks.listBank):
        print(f"{idx + 1}. {bank.bankName} | {bank.bankCode}")

    bank_code = input("Select the bank code eg 'MB': ").strip().upper()

    # Find the selected bank by bank code | bank.bankCode == bank_code
    bank_to = next(
        (bank for bank in banks.listBank if bank.bankCode == bank_code), None
    )

    if not bank_to:
        print("Invalid bank code selected.")
        exit(1)

    return bank_to


def get_src_account(mb: mbbank.MBBank):
    """
    Prompt user to select source account for transfer.
    """
    your_account = mb.getBalance()
    accounts = [acc for acc in your_account.acct_list]
    for idx, acc in enumerate(accounts):
        print(
            f"{idx + 1}. {acc.acctNo} - {acc.acctAlias} - Balance: {acc.currentBalance} {your_account.currencyEquivalent}"
        )
    acc_num = int(input("Select the account number to transfer from: ")) - 1
    return accounts[acc_num].acctNo


src_account = get_src_account(mb)
bank_to = get_bank_to(mb)
to_acc = input("Enter the recipient account number or nickname: ")
amount = int(input("Enter the amount to transfer: "))
message = input("Enter a message for the transfer: ")

transfer_ctx = mb.makeTransferAccountToAccount(
    src_account=src_account,
    dest_account=to_acc,
    bank_code=bank_to.bankCode,
    amount=amount,
    message=message,
)

auth_method = get_auth_method(mb)
auth_code = input(f"Enter the code for {auth_method.name}: ").strip()

qr = qrcode.make(transfer_ctx.get_qr_code())
qr.show()

print(transfer_ctx.transfer(otp=auth_code, auth_type=auth_method))
