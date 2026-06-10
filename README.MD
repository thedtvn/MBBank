# MBBank API for Python

An unofficial, lightweight Python API wrapper for the "Military Commercial Joint Stock Bank" (MBBank) personal accounts.

> [!WARNING]
> This library is unofficial and not endorsed by MBBank. Use it at your own risk.

## Features

- **Login**: Authenticate with your MBBank credentials.
- **Balance**: Check account balances.
- **Transaction History**: Retrieve transaction history for your accounts.
- **Transfer**: Perform money transfers to another account*.
- **Async Support**: Includes asynchronous capabilities for better performance.

> [!NOTE]
> Transfer feature requires MBBank APP on your phone to scan OTP code and confirm the transfer.

## Installation

### From PyPI

```bash
pip install mbbank-lib
```

### From Source (Development Version)

```bash
pip install git+https://github.com/thedtvn/MBBank
```

## Requirements

- Python 3.x
- [onnxruntime-gpu](https://onnxruntime.ai/getting-started) (Optional, for CUDA GPU support)

## Quick Start

Here is a simple example of how to log in and fetch your account balance:

```python
import mbbank


def main():
    username = "YOUR_USERNAME"
    password = "YOUR_PASSWORD"

    try:
        mb = mbbank.MBBank(username=username, password=password)

        # Get balance information
        balance_info = mb.getBalance()

        if balance_info.acct_list:
            print(f"Login successful! Found {len(balance_info.acct_list)} account(s).")
            for acct in balance_info.acct_list:
                print(f"Account: {acct.acctNo} - Balance: {acct.currentBalance} {acct.currency}")
        else:
            print("Login successful, but no accounts found.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
```

For more examples, check the [examples directory](https://github.com/thedtvn/MBBank/tree/main/examples)
or [docs](http://mbbank.rtfd.io/)

## Documentation

For detailed documentation and FAQ, visit: [http://mbbank.rtfd.io/](http://mbbank.rtfd.io/)

## Related Projects

- [Payment QR Code Generator (vietqr.io)](https://vietqr.io/)
- [MBBank JS API](https://github.com/CookieGMVN/MBBank)
- [MBBank OCR](https://github.com/thedtvn/mbbank-capcha-ocr)
- [MBBank Captcha Dataset](https://www.kaggle.com/datasets/cookiegmvn/mbbank-captcha-images)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not affiliated with MBBank. Use it responsibly and at your own risk.

The author is not liable for any damage or loss resulting from the use of this library.

Always ensure you comply with MBBank's terms of service and security guidelines when using this API.

## Legal

Any takedown requests or legal problems from MBBank can contact the author at:

- Email: mbbanklib-legal@thedt.id.vn
