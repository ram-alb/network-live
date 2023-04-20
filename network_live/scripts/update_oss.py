from dotenv import load_dotenv
from network_live.main import update_oss

load_dotenv()


def update_wcdma():
    print(update_oss('WCDMA'))
