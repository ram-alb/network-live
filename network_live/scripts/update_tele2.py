from dotenv import load_dotenv
from network_live.main import update_tele2

load_dotenv()


def update_lte():
    print(update_tele2('LTE'))


def update_wcdma():
    print(update_tele2('WCDMA'))


def update_gsm():
    print(update_tele2('GSM'))
