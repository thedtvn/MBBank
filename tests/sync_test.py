import os
import sys
import qrcode

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mbbank import MBBank

username = os.getenv("MBBANK_USERNAME")
password = os.getenv("MBBANK_PASSWORD")

if not username or not password:
    print("Please set MBBANK_USERNAME and MBBANK_PASSWORD environment variables.")
    sys.exit(1)

mb = MBBank(username=username, password=password)
# TODO: Rework on test and put more examples
