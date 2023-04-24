from dotenv import load_dotenv
from network_live.main import update_zte

load_dotenv()


def update_wcdma():
    """Update Network Live with ZTE wcdma cells."""
    print(update_zte('WCDMA'))


def update_gsm():
    """Update Network Live with ZTE gsm cells."""
    print(update_zte('GSM'))
