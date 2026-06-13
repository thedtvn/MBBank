# requires 'qrcode[pil]' package for QR code generation
import qrcode  # ty: ignore

import mbbank
from mbbank.modals import AccountTransfer, AuthListItem, Bank


def get_src_account(mb: mbbank.MBBank) -> str:
    """
    Prompt the user to select a source account for transfers.
    """
    your_account = mb.getBalance()
    accounts = [acc for acc in your_account.acct_list]
    
    print("\nYour accounts:")
    for idx, acc in enumerate(accounts):
        print(
            f"{idx + 1}. {acc.acctNo} - {acc.acctAlias} - Balance: {acc.currentBalance} {your_account.currencyEquivalent}"
        )
    
    acc_num = int(input("Select the account number to transfer from: ")) - 1
    return accounts[acc_num].acctNo


def get_bank(mb: mbbank.MBBank) -> Bank:
    """
    Prompt user to select a bank for transfers.
    """
    banks = mb.getBankList().listBank

    print("\nAvailable banks:")
    for idx, bank in enumerate(banks):
        print(f"{idx + 1}. {bank.bankNameEN} ({bank.bankCode}) (smlCode: {bank.smlCode})")

    bank_code = input("Enter bank code (eg. 'MB'): ")
    for bank in banks:
        if bank.bankCode == bank_code:
            return bank
    raise ValueError(f"Bank code '{bank_code}' not found.")


def get_transfer_list(mb: mbbank.MBBank) -> list[AccountTransfer]:
    """
    Prompt user to input multiple transfer details.
    """
    transfers = []
    
    num_transfers = int(input("\nHow many transfers do you want to make: "))
    
    for i in range(num_transfers):
        print(f"\n--- Transfer {i + 1}/{num_transfers} ---")
        credit_account = input("Recipient account number: ").strip()
        bank_code = get_bank(mb).smlCode
        amount = int(input("Amount: "))
        description = input("Message: ").strip()
        
        transfers.append(AccountTransfer(
            benBankCode=bank_code,
            amount=amount,
            creditAccount=credit_account,
            description=description
        ))
    
    return transfers


def get_auth_method(transfer_ctx: mbbank.BulkTransferContext) -> AuthListItem:
    """
    Prompt user to select authentication method for transfers.
    """
    auth_methods = transfer_ctx.get_auth_list()

    print("\nAvailable authentication methods:")
    for idx, method in enumerate(auth_methods.authList):
        print(f"{idx + 1}. {method.name}")

    auth_idx = int(input("Select the authentication method number: ")) - 1
    return auth_methods.authList[auth_idx]


def preview_transfers(transfers: list[AccountTransfer], description: str) -> None:
    """
    Display a summary of all pending transfers.
    """
    print("\n" + "="*80)
    print("BULK TRANSFER PREVIEW")
    print("="*80)
    print(f"Description: {description}")
    print()
    
    total_amount = sum(t.amount for t in transfers)
    
    for idx, transfer in enumerate(transfers, 1):
        print(f"{idx}. To: {transfer.creditAccount} (Bank: {transfer.benBankCode})")
        print(f"   Amount: {transfer.amount:,} VND")
        print(f"   Message: {transfer.description}")
        print()
    
    print(f"Total transfers: {len(transfers)}")
    print(f"Total amount: {total_amount:,} VND")
    print("="*80)


def main():
    # Login
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    mb = mbbank.MBBank(username=username, password=password)
    
    # Select source account
    src_account = get_src_account(mb)
    
    # Get transfer list
    transfers = get_transfer_list(mb)
    
    if not transfers:
        print("No transfers to process.")
        return
    
    # Get bulk transfer description
    description = input("\nEnter description for this bulk transfer: ").strip()
    
    # Preview transfers
    preview_transfers(transfers, description)

    
    # Create bulk transfer context
    transfer_ctx = mb.makeBulkTransfer(
        src_account=src_account,
        dest_accounts=transfers,
        description=description
    )

    # Get authentication method
    auth_method = get_auth_method(transfer_ctx)
    
    # Show QR code for authentication
    qr = qrcode.make(transfer_ctx.get_qr_code())
    qr.show()
    
    # Get OTP
    auth_code = input(f"\nEnter the code for {auth_method.name}: ").strip()
    
    # Execute bulk transfer
    print("\nProcessing bulk transfer...")
    transfer_ctx.transfer(otp=auth_code, auth_type=auth_method)
    
    print("\n" + "="*80)
    print("BULK TRANSFER RESULT")
    print("="*80)
    print(f"Total Amount: {transfer_ctx.amount} VND")
    print("="*80)
    print("\n✅ Bulk transfer completed successfully!")


if __name__ == "__main__":
    main()
