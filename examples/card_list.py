import getpass
import mbbank


def main():
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    try:
        mb = mbbank.MBBank(username=username, password=password)
    except Exception as e:
        print(f"Login failed: {e}")
        return

    try:
        print("Fetching card list...")
        cards_response = mb.getCardList()

        if not cards_response.cardList:
            print("No cards found.")
        else:
            print("\nCard List:")
            print("-" * 60)
            print(f"{'Card Number':<20} | {'Type':<20} | {'Status'}")
            print("-" * 60)
            for card in cards_response.cardList:
                # Adjust fields based on actual Card model
                card_number = getattr(card, "cardNo", "N/A")
                card_type = getattr(card, "cardModule", "N/A")  # or cardClass, cardType
                status = getattr(card, "cardStatus", "N/A")

                print(f"{str(card_number):<20} | {str(card_type):<20} | {status}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
