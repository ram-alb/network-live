from dotenv import load_dotenv
from network_live.main import update_tele2

load_dotenv()


def update_lte():
    """Update Network Live with Tele2 LTE cells."""
    print(update_tele2('LTE'))


def update_wcdma():
    """Update Network Live with Tele2 WCDMA cells."""
    print(update_tele2('WCDMA'))


def update_gsm():
    """Update Network Live with Tele2 GSM cells."""
    print(update_tele2('GSM'))
