from dotenv import load_dotenv
from network_live.main import update_zte

load_dotenv()


def update_wcdma():
    print(update_zte('WCDMA'))


def update_gsm():
    print(update_zte('GSM'))
