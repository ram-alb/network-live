from dotenv import load_dotenv
from network_live.main import update_beeline

load_dotenv()


def update_huawei_lte():
    print(update_beeline('Huawei', 'LTE'))


def update_huawei_wcdma():
    print(update_beeline('Huawei', 'WCDMA'))


def update_nokia_lte():
    print(update_beeline('Nokia', 'LTE'))


def update_nokia_wcdma():
    print(update_beeline('Nokia', 'WCDMA'))


def update_nokia_gsm():
    print(update_beeline('Nokia', 'GSM'))
