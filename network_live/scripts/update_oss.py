from dotenv import load_dotenv
from network_live.main import update_oss

load_dotenv()


def update_wcdma():
    """Update Network Live with OSS wcdma cells."""
    print(update_oss('WCDMA'))


def update_gsm():
    """Update Network Live with OSS gsm cells."""
    print(update_oss('GSM'))
